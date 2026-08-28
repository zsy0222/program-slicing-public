"""
Program Dependence Graph construction.

Builds PDG from a flattened statement list:
1. Create nodes from statements
2. Build Control Flow Graph
3. Compute control dependencies (post-dominator analysis)
4. Compute data dependencies (reaching definitions, iterative fixpoint)

The PDG edges represent LOGICAL (semantic) dependencies, not variable-name matches:
- Data edge S1→S2: S1 defines v, S2 uses v, no intervening redefinition of v
  on the CFG path from S1 to S2
- Control edge C→S: statement S's execution depends on condition C evaluating
  a particular way (true/false branch of if/while/for)
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple

from .models import PDGNode, PDGEdge, PDG, NodeType, EdgeType


def build_pdg(
    statements: List[Tuple[int, str, NodeType, Set[str], Set[str]]],
    method_name: str = "",
    source_code: str = "",
    param_vars: Set[str] = None,
) -> PDG:
    """
    Build a Program Dependence Graph from a list of statements.

    Each statement is a tuple: (line, code, node_type, defined_vars, used_vars).
    """
    if not statements:
        return PDG(method_name=method_name, source_code=source_code)

    pdg = PDG(method_name=method_name, source_code=source_code)
    n = len(statements)

    # Step 1: Create statement nodes (IDs 1..n)
    stmt_ids = list(range(1, n + 1))
    for i, stmt in enumerate(statements):
        line, code, node_type, defined, used = stmt[0], stmt[1], stmt[2], stmt[3], stmt[4]
        node = PDGNode(
            id=stmt_ids[i],
            line=line,
            code=code,
            node_type=node_type,
            defined_vars=defined,
            used_vars=used,
        )
        pdg.add_node(node)

    # Step 2: ENTRY node (id=0)
    entry = PDGNode(
        id=0,
        line=0,
        code=f"ENTRY: {method_name}",
        node_type=NodeType.ENTRY,
        defined_vars=param_vars or set(),
        used_vars=set(),
    )
    pdg.entry_node_id = 0
    pdg.add_node(entry)

    # Step 3: EXIT node
    exit_id = n + 1
    exit_node = PDGNode(
        id=exit_id,
        line=0,
        code="EXIT",
        node_type=NodeType.EXIT,
        defined_vars=set(),
        used_vars=set(),
    )
    pdg.exit_node_id = exit_id
    pdg.add_node(exit_node)

    # Step 4: Build CFG (intra-procedural, structured control flow)
    cfg_succ, cfg_pred = _build_cfg(statements, stmt_ids, pdg.entry_node_id, pdg.exit_node_id)

    # Step 5: Compute control dependencies on CFG
    _compute_control_deps(pdg, cfg_succ, cfg_pred)

    # Step 6: Compute data dependencies (iterative reaching definitions)
    _compute_data_deps(pdg, statements, stmt_ids, cfg_succ, cfg_pred)

    return pdg


def _build_cfg(
    statements: List, stmt_ids: List[int], entry_id: int, exit_id: int,
) -> Tuple[Dict[int, List[int]], Dict[int, List[int]]]:
    """
    Build Control Flow Graph for structured code (no goto).

    Handles if-else via tuple skip info: when a statement has skip > 0,
    its sequential successor skips the next N statements (the else body).
    """
    n = len(statements)
    cfg_succ: Dict[int, List[int]] = defaultdict(list)
    cfg_pred: Dict[int, List[int]] = defaultdict(list)

    def add_edge(frm, to):
        cfg_succ[frm].append(to)
        cfg_pred[to].append(frm)

    # ENTRY → first statement
    add_edge(entry_id, stmt_ids[0])

    # Scan through statements
    i = 0
    while i < n:
        sid = stmt_ids[i]
        # Handle both 6-tuple and 7-tuple formats
        stmt = statements[i]
        _, _, node_type, _, _ = stmt[0], stmt[1], stmt[2], stmt[3], stmt[4]
        skip_next = stmt[6] if len(stmt) > 6 else 0

        if node_type == NodeType.RETURN:
            add_edge(sid, exit_id)
            i += 1
            continue

        if node_type == NodeType.CONDITION:
            # True branch: CONDITION → next statement (body)
            if i + 1 < n:
                add_edge(sid, stmt_ids[i + 1])

            # False branch: CONDITION → statement after controlled block
            after = _find_block_end(statements, i)
            if after < n:
                add_edge(sid, stmt_ids[after])
            else:
                add_edge(sid, exit_id)

            i += 1
            continue

        # Sequential: sid → next (unless skip_next says otherwise)
        next_i = i + 1 + skip_next
        if next_i < n:
            add_edge(sid, stmt_ids[next_i])
        else:
            add_edge(sid, exit_id)
        i += 1

    return cfg_succ, cfg_pred


def _find_block_end(statements: List, cond_idx: int) -> int:
    """
    Find the index of the first statement AFTER the block controlled
    by the condition at cond_idx.

    Simple heuristic: for structured if/while (no else), the condition
    controls the immediately following non-condition statement (i+1).
    The false-branch target is i+2.

    For nested conditions or multi-statement bodies, this is approximate.
    A full implementation would track block nesting explicitly.
    """
    return min(cond_idx + 2, len(statements))


def _compute_control_deps(
    pdg: PDG,
    cfg_succ: Dict[int, List[int]],
    cfg_pred: Dict[int, List[int]],
):
    """
    Compute control dependencies using post-dominator analysis.

    Y is control-dependent on X iff:
      - X has >= 2 outgoing CFG edges (branch point)
      - Y post-dominates one successor of X
      - Y does NOT post-dominate X itself
    """
    all_nodes = set(pdg.nodes.keys())

    # Compute post-dominators: D post-dominates N iff
    # every path from N to EXIT goes through D.
    # Equivalent: D dominates N in the REVERSE CFG.

    pdom: Dict[int, Set[int]] = {}

    # Initialize
    for n in all_nodes:
        pdom[n] = all_nodes.copy() if n != pdg.exit_node_id else {pdg.exit_node_id}

    # Iterative fixpoint (reverse CFG dominators = post-dominators)
    # PDOM(n) = {n} ∪ ⋂_{s∈succ(n)} PDOM(s)   ← INTERSECTION, not union!
    changed = True
    while changed:
        changed = False
        for n in all_nodes:
            if n == pdg.exit_node_id:
                continue
            succs = cfg_succ.get(n, [])
            if not succs:
                new_pdom = {n}
            else:
                # Intersection of all successors' post-dominator sets
                intersect = pdom.get(succs[0], set()).copy()
                for s in succs[1:]:
                    intersect &= pdom.get(s, set())
                new_pdom = {n} | intersect
            if new_pdom != pdom.get(n):
                pdom[n] = new_pdom
                changed = True

    # For each branch node X (>=2 successors), find control-dependent nodes
    for x in all_nodes:
        x_succs = cfg_succ.get(x, [])
        if len(x_succs) < 2:
            continue

        for y in all_nodes:
            if y == x:
                continue
            y_in_pdom_x = y in pdom.get(x, set())

            for z in x_succs:
                if y in pdom.get(z, set()) and not y_in_pdom_x:
                    pdg.add_edge(x, y, EdgeType.CONTROL_DEP)
                    break


def _compute_data_deps(
    pdg: PDG,
    statements: List,
    stmt_ids: List[int],
    cfg_succ: Dict[int, List[int]],
    cfg_pred: Dict[int, List[int]],
):
    """
    Compute data dependencies using iterative reaching definitions.

    For each node S:
    - GEN[S] = {(v, S)} for each variable v that S defines
    - KILL[S] = {(v, D)} for all definitions D of v from any node
    - IN[S] = ⋃_{P in pred(S)} OUT[P]
    - OUT[S] = GEN[S] ∪ (IN[S] - KILL[S])

    Then for each used variable v in S, add data dependency edges
    from every definition (v, D) in IN[S].
    """
    n = len(statements)
    node_ids = [pdg.entry_node_id] + stmt_ids + [pdg.exit_node_id]

    # Collect all variables
    all_vars = set()
    for node in pdg.nodes.values():
        all_vars.update(node.defined_vars)
        all_vars.update(node.used_vars)

    # For each node, compute GEN and KILL
    # Each definition is (variable, defining_node_id)
    gen: Dict[int, Set[Tuple[str, int]]] = defaultdict(set)
    kill: Dict[int, Set[Tuple[str, int]]] = defaultdict(set)

    for nid in node_ids:
        if nid == pdg.entry_node_id:
            node = pdg.nodes[nid]
            for v in node.defined_vars:
                gen[nid].add((v, nid))
        elif nid == pdg.exit_node_id:
            pass  # EXIT generates nothing
        else:
            node = pdg.nodes.get(nid)
            if node is None:
                continue
            for v in node.defined_vars:
                gen[nid].add((v, nid))

    # KILL for each variable: all (v, any_node) pairs
    for v in all_vars:
        for nid in node_ids:
            node = pdg.nodes.get(nid)
            if node and v in node.defined_vars:
                # This node kills all other definitions of v
                for other_nid in node_ids:
                    if other_nid != nid:
                        kill[nid].add((v, other_nid))

    # Iterative fixpoint for IN/OUT
    in_set: Dict[int, Set[Tuple[str, int]]] = defaultdict(set)
    out_set: Dict[int, Set[Tuple[str, int]]] = defaultdict(set)

    changed = True
    iteration = 0
    while changed and iteration < 100:
        changed = False
        iteration += 1
        for nid in node_ids:
            # IN = union of OUT of all CFG predecessors
            new_in = set()
            for p in cfg_pred.get(nid, []):
                new_in.update(out_set.get(p, set()))

            # For ENTRY, IN is empty
            if nid == pdg.entry_node_id:
                new_in = set()

            if new_in != in_set.get(nid):
                in_set[nid] = new_in
                changed = True

            # OUT = GEN ∪ (IN - KILL)
            new_out = set(gen.get(nid, set()))
            for defn in new_in:
                _, var_def = defn
                # Check if killed
                if defn not in kill.get(nid, set()):
                    new_out.add(defn)

            if new_out != out_set.get(nid):
                out_set[nid] = new_out
                changed = True

    # Add data dependency edges: for each used variable in S,
    # add edges from reaching definitions in IN[S]
    for nid in node_ids:
        if nid in (pdg.entry_node_id, pdg.exit_node_id):
            continue
        node = pdg.nodes.get(nid)
        if node is None:
            continue

        for used_var in node.used_vars:
            reaching_defs = {d for (v, d) in in_set.get(nid, set()) if v == used_var}
            for def_id in reaching_defs:
                if def_id != nid:
                    pdg.add_edge(def_id, nid, EdgeType.DATA_DEP, used_var)
