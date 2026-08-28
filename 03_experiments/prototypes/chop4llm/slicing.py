"""
Program Slicing Algorithms on PDG.

Implements three slicing operations:
1. Backward slice: all nodes that can reach a sink node via PDG edges.
2. Forward slice: all nodes reachable from a source node via PDG edges.
3. Chop (Jackson & Rollins 1994): restricted reachability — nodes that lie
   on a PDG path FROM any source TO any sink.

Key difference from simple intersection:
    Forward(s) ∩ Backward(t) can include nodes that are on UNRELATED paths.
    Chop(s, t) = nodes on paths that start at s AND end at t.

Algorithm (two-phase):
    Phase 1: Compute F = forward_reachable(source_nodes)
    Phase 2: In PDG restricted to F, compute backward_reachable(sink_nodes)
    Result = backward_reachable ∩ F = nodes on s→...→t paths
"""

from collections import deque
from typing import List, Optional, Set

from .models import PDG, PDGNode, EdgeType


def forward_slice(pdg: PDG, source_ids: Set[int]) -> Set[int]:
    """
    Compute all nodes forward-reachable from source_ids via PDG edges.

    Follows data edges (def→use) and control edges (condition→body)
    in the forward direction.
    """
    if not source_ids:
        return set()

    # Ensure adjacency is built
    pdg._build_adjacency()

    visited = set()
    queue = deque(source_ids)

    while queue:
        node_id = queue.popleft()
        if node_id in visited:
            continue
        if node_id not in pdg.nodes:
            continue
        visited.add(node_id)
        for succ in pdg.successors(node_id):
            if succ not in visited:
                queue.append(succ)

    return visited


def backward_slice(pdg: PDG, sink_ids: Set[int]) -> Set[int]:
    """
    Compute all nodes that can reach sink_ids via PDG edges.

    Follows edges in reverse: from use to def (data edges backwards)
    and from body to condition (control edges backwards).
    """
    if not sink_ids:
        return set()

    pdg._build_adjacency()

    visited = set()
    queue = deque(sink_ids)

    while queue:
        node_id = queue.popleft()
        if node_id in visited:
            continue
        if node_id not in pdg.nodes:
            continue
        visited.add(node_id)
        for pred in pdg.predecessors(node_id):
            if pred not in visited:
                queue.append(pred)

    return visited


def chop(
    pdg: PDG,
    source_ids: Set[int],
    sink_ids: Set[int],
) -> Set[int]:
    """
    Chop: find all nodes on PDG paths FROM any source TO any sink.

    This is the proper Chop algorithm (Jackson & Rollins 1994),
    NOT a simple intersection of forward and backward slices.

    Algorithm:
        1. F = forward_slice(PDG, source_ids)
        2. Only keep sink_ids that are actually in F (reachable from source)
        3. PDG' = PDG restricted to nodes in F
        4. B = backward_slice(PDG', sink_ids ∩ F)
        5. Chop = B  (equivalently: F ∩ B)

    This ensures every node in the result belongs to a path that
    starts at a source and ends at a sink.
    """
    if not source_ids or not sink_ids:
        return set()

    # Phase 1: Forward slice from all sources
    forward_nodes = forward_slice(pdg, source_ids)

    # Filter sink_ids to those reachable from sources
    reachable_sinks = sink_ids & forward_nodes
    if not reachable_sinks:
        # No path from source to sink exists
        return set()

    # Phase 2: Backward slice restricted to forward_nodes
    # Build a subgraph adjacency restricted to forward_nodes
    pdg._build_adjacency()

    visited = set()
    queue = deque(reachable_sinks)

    while queue:
        node_id = queue.popleft()
        if node_id in visited:
            continue
        if node_id not in forward_nodes:
            continue  # Only traverse within forward-reachable subgraph
        visited.add(node_id)
        for pred in pdg.predecessors(node_id):
            if pred not in visited and pred in forward_nodes:
                queue.append(pred)

    return visited


def compute_dependency_chains(
    pdg: PDG,
    chop_nodes: Set[int],
    source_ids: Set[int],
    sink_ids: Set[int],
) -> List[List[PDGNode]]:
    """
    Extract dependency chains from source to sink through chop nodes.

    Uses BFS from each source to find paths to sinks within the chop set.
    Returns a list of dependency chains (each chain is a list of nodes).
    """
    chains = []
    pdg._build_adjacency()

    for src_id in source_ids:
        if src_id not in chop_nodes:
            continue

        # BFS to find shortest paths from src to each sink
        for sink_id in sink_ids:
            if sink_id not in chop_nodes:
                continue
            if src_id == sink_id:
                chains.append([pdg.nodes[src_id]])
                continue

            # Simple BFS path finding within chop nodes
            queue = deque([(src_id, [src_id])])
            visited_paths = {src_id}

            while queue:
                cur_id, path = queue.popleft()
                if cur_id == sink_id:
                    chains.append([pdg.nodes[nid] for nid in path])
                    break

                for succ in pdg.successors(cur_id):
                    if succ in chop_nodes and succ not in visited_paths:
                        visited_paths.add(succ)
                        queue.append((succ, path + [succ]))

    return chains


def backward_slice_from_line(pdg: PDG, sink_line: int) -> Set[int]:
    """Convenience: backward slice from a source line number."""
    sink_ids = {nid for nid, node in pdg.nodes.items()
                 if node.line == sink_line}
    return backward_slice(pdg, sink_ids)


def forward_slice_from_line(pdg: PDG, source_line: int) -> Set[int]:
    """Convenience: forward slice from a source line number."""
    source_ids = {nid for nid, node in pdg.nodes.items()
                   if node.line == source_line}
    return forward_slice(pdg, source_ids)


def chop_from_lines(
    pdg: PDG,
    source_lines: List[int],
    sink_lines: List[int],
) -> Set[int]:
    """Convenience: chop using source and sink line numbers."""
    source_ids = set()
    for nid, node in pdg.nodes.items():
        if node.line in source_lines:
            source_ids.add(nid)

    sink_ids = set()
    for nid, node in pdg.nodes.items():
        if node.line in sink_lines:
            sink_ids.add(nid)

    return chop(pdg, source_ids, sink_ids)


def describe_slice(pdg: PDG, slice_node_ids: Set[int]) -> str:
    """Generate a human-readable description of a slice."""
    nodes = [pdg.nodes[nid] for nid in slice_node_ids
             if nid in pdg.nodes and pdg.nodes[nid].line > 0]
    nodes.sort(key=lambda n: n.line)

    lines = []
    lines.append(f"Slice contains {len(nodes)} statements:")
    for node in nodes:
        deps = []
        for edge in pdg.edges:
            if edge.target == node.id and edge.source in slice_node_ids:
                dep_type = "D" if edge.edge_type == EdgeType.DATA_DEP else "C"
                var_str = f"({edge.variable})" if edge.variable else ""
                deps.append(f"{dep_type}{var_str}←{edge.source}")
        dep_str = f" [{', '.join(deps)}]" if deps else ""
        lines.append(f"  L{node.line}: {node.code[:60]}{dep_str}")

    return '\n'.join(lines)
