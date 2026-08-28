"""
LLM Prompt Formatter

Formats program slice results into structured prompts for LLM analysis.
Supports template-based formatting with annotation of dependency types.
"""

import os
from typing import Dict, List, Optional

from .models import PDG, PDGNode, EdgeType, SliceResult


# ─── Default Prompt Templates ──────────────────────────────────────────────

TEMPLATE_BUG_FIND = """## Bug Localization Task

You are analyzing a **program slice** — a subset of code containing ONLY the
statements that have a logical dependency relationship with a suspected bug.

### Slice Statistics
- Original method: {method_name}
- Original statements: {original_count}
- Sliced statements: {sliced_count}
- **Code reduction: {compression_pct:.1f}%**

### Dependency Chain (Source → Sink)
{chains_description}

### Sliced Code
```
{annotated_code}
```

### Your Task
The code above has been reduced via **program chop** — bidirectional slicing that
follows data-flow (def-use chains) and control-flow (branch conditions) to include
ONLY statements that can propagate a value from source to sink.

{dependency_legend}

For each statement, reason about:
1. Could this statement cause the observed bug?
2. What value would it produce in normal vs. faulty execution?
3. If this IS the bug location, what fix do you suggest?

Provide your analysis as:
1. **Most suspicious statement(s)** with line numbers
2. **Reasoning** for each (why it explains the symptom)
3. **Suggested fix** with corrected code
"""

TEMPLATE_CODE_UNDERSTAND = """## Code Understanding Task

You are analyzing a **program slice** — a logical subset of code extracted via
bidirectional program slicing (Chop). This slice contains ONLY the statements
that participate in the data/control flow from a specific input to a specific output.

### Slice Statistics
- Original method: {method_name}
- Original statements: {original_count}
- Sliced statements: {sliced_count}
- **Code reduction: {compression_pct:.1f}%**

### Sliced Code
```
{annotated_code}
```

### Dependency Information
{dependency_legend}

{dependency_detail}

### Your Task
1. Summarize what this slice does (from source inputs to sink outputs)
2. Identify the key data transformations along the path
3. Note any suspicious or error-prone patterns
"""


def _get_dependency_legend() -> str:
    """Return a legend explaining annotation markers."""
    return """### Annotation Legend
Each line is annotated with its dependency type:
- `[D:varname]` — Data dependency: this line uses variable `varname` defined by the referenced line
- `[C]` — Control dependency: this line's execution depends on a condition at the referenced line
- `[source]` / `[sink]` — Start/end points of the slice"""


def format_slice_for_llm(
    pdg: PDG,
    slice_node_ids: set,
    source_ids: set = None,
    sink_ids: set = None,
    template: str = "bug_find",
    original_source: str = "",
) -> str:
    """
    Format a slice result into an LLM-ready prompt.

    Args:
        pdg: The Program Dependence Graph.
        slice_node_ids: Set of node IDs in the slice.
        source_ids: Source node IDs for the chop.
        sink_ids: Sink node IDs for the chop.
        template: Template name ('bug_find' or 'code_understand').
        original_source: Original full source code.

    Returns:
        Formatted string ready to paste into an LLM conversation.
    """
    source_ids = source_ids or set()
    sink_ids = sink_ids or set()

    # Filter to nodes with actual code lines
    slice_nodes = sorted(
        [pdg.nodes[nid] for nid in slice_node_ids
         if nid in pdg.nodes and pdg.nodes[nid].line > 0],
        key=lambda n: n.line,
    )

    # Count original statements
    original_nodes = [n for n in pdg.nodes.values() if n.line > 0]

    # Build annotated code
    annotated = _build_annotated_code(slice_nodes, source_ids, sink_ids, pdg)

    # Build chains description
    chains_desc = _build_chains_description(pdg, slice_node_ids, source_ids, sink_ids)

    # Dependency detail
    dep_detail = _build_dependency_detail(slice_node_ids, pdg)

    # Template variables
    variables = {
        "method_name": pdg.method_name or "unknown",
        "original_count": len(original_nodes),
        "sliced_count": len(slice_nodes),
        "compression_pct": (1 - len(slice_nodes) / max(len(original_nodes), 1)) * 100,
        "annotated_code": annotated,
        "chains_description": chains_desc,
        "dependency_legend": _get_dependency_legend(),
        "dependency_detail": dep_detail,
    }

    if template == "bug_find":
        return TEMPLATE_BUG_FIND.format(**variables)
    else:
        return TEMPLATE_CODE_UNDERSTAND.format(**variables)


def _build_annotated_code(
    slice_nodes: List[PDGNode],
    source_ids: set,
    sink_ids: set,
    pdg: PDG,
) -> str:
    """Build annotated source code with dependency markers."""
    lines = []

    for node in slice_nodes:
        # Determine annotations
        annotations = []

        if node.id in source_ids:
            annotations.append("source")
        if node.id in sink_ids:
            annotations.append("sink")

        # Find incoming edges from within the slice
        for edge in pdg.edges:
            if edge.target == node.id and edge.source in {n.id for n in slice_nodes}:
                if edge.edge_type == EdgeType.DATA_DEP:
                    annotations.append(f"D:{edge.variable or '?'}")
                elif edge.edge_type == EdgeType.CONTROL_DEP:
                    annotations.append("C")

        ann_str = f"  // [{', '.join(annotations)}]" if annotations else ""
        lines.append(f"L{node.line:04d}: {node.code}{ann_str}")

    return '\n'.join(lines)


def _build_chains_description(
    pdg: PDG,
    slice_node_ids: set,
    source_ids: set,
    sink_ids: set,
) -> str:
    """Build a textual description of dependency chains."""
    parts = []

    for src_id in source_ids:
        if src_id not in pdg.nodes:
            continue
        src_node = pdg.nodes[src_id]
        for sink_id in sink_ids:
            if sink_id not in pdg.nodes:
                continue
            sink_node = pdg.nodes[sink_id]
            parts.append(f"  L{src_node.line} → ... → L{sink_node.line}")

    if not parts:
        parts.append("  (no source→sink chain identified)")

    return '\n'.join(parts)


def _build_dependency_detail(
    slice_node_ids: set,
    pdg: PDG,
) -> str:
    """Build detailed dependency information for each sliced statement."""
    lines = ["### Statement Dependencies (detail)", ""]

    sorted_nodes = sorted(
        [pdg.nodes[nid] for nid in slice_node_ids if nid in pdg.nodes],
        key=lambda n: n.line,
    )

    for node in sorted_nodes:
        if node.line <= 0:
            continue

        # What does this node depend on (incoming edges within slice)?
        depends_on = []
        for edge in pdg.edges:
            if edge.target == node.id and edge.source in slice_node_ids:
                src_node = pdg.nodes.get(edge.source)
                if src_node and src_node.line > 0:
                    if edge.edge_type == EdgeType.DATA_DEP:
                        depends_on.append(
                            f"L{src_node.line} defines `{edge.variable}`"
                        )
                    elif edge.edge_type == EdgeType.CONTROL_DEP:
                        depends_on.append(
                            f"L{src_node.line} controls execution"
                        )

        # What depends on this node (outgoing edges within slice)?
        affects = []
        for edge in pdg.edges:
            if edge.source == node.id and edge.target in slice_node_ids:
                tgt_node = pdg.nodes.get(edge.target)
                if tgt_node and tgt_node.line > 0:
                    if edge.edge_type == EdgeType.DATA_DEP:
                        affects.append(
                            f"L{tgt_node.line} uses `{edge.variable}`"
                        )
                    elif edge.edge_type == EdgeType.CONTROL_DEP:
                        affects.append(
                            f"L{tgt_node.line} (controlled)"
                        )

        dep_str = "; ".join(depends_on) if depends_on else "(entry)"
        aff_str = "; ".join(affects) if affects else "(exit/sink)"
        lines.append(f"**L{node.line}** `{node.code[:50]}`")
        lines.append(f"  ← depends on: {dep_str}")
        lines.append(f"  → affects: {aff_str}")
        lines.append("")

    return '\n'.join(lines)
