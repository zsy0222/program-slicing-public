"""
Chop4LLM Public API

Clean, simple interface for program slicing + LLM integration.

Borrowed from GitIngest: clean single-function API design.
Borrowed from CLDK/WALA: PDG-based logical dependency analysis.
Own contribution: Chop algorithm + slice-to-LLM formatting.

Usage:
    from chop4llm import chop_method, ChopResult

    result = chop_method(java_source, sink_line=42, source_line=10)
    print(result.llm_prompt)

    # Only backward slice:
    result = chop_method(java_source, sink_line=42)

    # Auto-detect sources:
    result = chop_method(java_source, sink_line=42, auto_source=True)
"""

from typing import Dict, List, Optional, Set

from .models import PDG, PDGNode, SliceResult
from .pdg import build_pdg
from .slicing import (
    backward_slice_from_line,
    forward_slice_from_line,
    chop_from_lines,
    compute_dependency_chains,
    describe_slice,
)
from .formatter import format_slice_for_llm
from .parser_java import parse_java_method, parse_java_file


class ChopResult:
    """
    Result of a chop operation.

    Contains both the raw slice data and the LLM-ready formatted prompt.
    """

    def __init__(
        self,
        pdg: PDG,
        slice_node_ids: Set[int],
        source_ids: Set[int],
        sink_ids: Set[int],
        original_source: str,
        llm_prompt: str,
        method_name: str = "",
    ):
        self.pdg = pdg
        self.slice_node_ids = slice_node_ids
        self.source_ids = source_ids
        self.sink_ids = sink_ids
        self.original_source = original_source
        self.llm_prompt = llm_prompt
        self.method_name = method_name

        # Compute statistics
        self.original_nodes = [n for n in pdg.nodes.values() if n.line > 0]
        self.slice_nodes = sorted(
            [pdg.nodes[nid] for nid in slice_node_ids
             if nid in pdg.nodes and pdg.nodes[nid].line > 0],
            key=lambda n: n.line,
        )
        self.original_count = len(self.original_nodes)
        self.sliced_count = len(self.slice_nodes)
        self.compression_pct = (
            (1 - self.sliced_count / max(self.original_count, 1)) * 100
        )

    @property
    def sliced_code(self) -> str:
        """Reconstructed source code containing only sliced statements."""
        return '\n'.join(node.code for node in self.slice_nodes)

    def describe(self) -> str:
        """Human-readable summary of the slice."""
        return describe_slice(self.pdg, self.slice_node_ids)

    def __repr__(self) -> str:
        return (
            f"ChopResult(method={self.method_name}, "
            f"original={self.original_count}, sliced={self.sliced_count}, "
            f"reduction={self.compression_pct:.1f}%)"
        )


def chop_method(
    source_code: str,
    sink_line: int,
    source_line: int = None,
    source_lines: List[int] = None,
    method_name: str = None,
    auto_source: bool = False,
    template: str = "bug_find",
) -> ChopResult:
    """
    Analyze a Java method and produce a chop slice for LLM consumption.

    Args:
        source_code: Java source code (a class containing the target method).
        sink_line: Line number of the bug/output/sink statement (1-based).
        source_line: Line number of the suspected source (input/assignment).
            If None, uses auto_source or pure backward slice.
        source_lines: Multiple source line numbers.
        method_name: Name of the method to analyze. Auto-detected if None.
        auto_source: If True and no source_line given, treat entry parameters
            as implicit sources (gives a backward slice from sink).
        template: LLM prompt template ('bug_find' or 'code_understand').

    Returns:
        ChopResult with slice data and LLM-ready prompt.
    """
    # Step 1: Parse and extract statements
    if method_name:
        statements = parse_java_method(source_code, method_name)
    else:
        methods = parse_java_file(source_code)
        if not methods:
            raise ValueError("No methods found in source code")
        # Pick the method that contains the sink line
        for mname, stmts in methods.items():
            for stmt in stmts:
                if stmt[0] == sink_line:  # stmt[0] is line number
                    statements = stmts
                    method_name = mname
                    break
            else:
                continue
            break
        else:
            # Default to first method
            method_name = list(methods.keys())[0]
            statements = methods[method_name]

    if not statements:
        raise ValueError(f"No statements found in method '{method_name}'")

    # Step 2: Build PDG
    # Extract parameter variables (first statement or method signature)
    param_vars = set()
    pdg = build_pdg(statements, method_name, source_code, param_vars)

    # Step 3: Determine source and sink node IDs
    sink_ids = _find_node_ids_by_line(pdg, sink_line)
    if not sink_ids:
        # Try closest line
        sink_ids = _find_closest_node_ids(pdg, sink_line)

    all_source_lines = list(source_lines or [])
    if source_line:
        all_source_lines.append(source_line)

    if all_source_lines:
        source_ids = set()
        for sl in all_source_lines:
            ids = _find_node_ids_by_line(pdg, sl)
            if not ids:
                ids = _find_closest_node_ids(pdg, sl)
            source_ids.update(ids)
    elif auto_source:
        # Use ENTRY node as implicit source
        source_ids = {pdg.entry_node_id}
    else:
        # Pure backward slice: source = ENTRY
        source_ids = {pdg.entry_node_id}

    # Step 4: Perform slicing
    if source_ids == {pdg.entry_node_id} and not auto_source and not all_source_lines:
        # Pure backward slice from sink
        slice_node_ids = _backward_slice_with_entry(pdg, sink_ids)
        source_ids = {pdg.entry_node_id}
    elif source_ids and sink_ids:
        # Chop: bidirectional restricted reachability
        slice_node_ids = chop_from_lines(
            pdg,
            [pdg.nodes[sid].line for sid in source_ids if sid in pdg.nodes],
            [pdg.nodes[tid].line for tid in sink_ids if tid in pdg.nodes],
        )
        if not slice_node_ids:
            # Fallback: at least backward slice
            slice_node_ids = _backward_slice_with_entry(pdg, sink_ids)
    else:
        slice_node_ids = _backward_slice_with_entry(pdg, sink_ids)

    # Step 5: Format for LLM
    llm_prompt = format_slice_for_llm(
        pdg=pdg,
        slice_node_ids=slice_node_ids,
        source_ids=source_ids,
        sink_ids=sink_ids,
        template=template,
        original_source=source_code,
    )

    return ChopResult(
        pdg=pdg,
        slice_node_ids=slice_node_ids,
        source_ids=source_ids,
        sink_ids=sink_ids,
        original_source=source_code,
        llm_prompt=llm_prompt,
        method_name=method_name or "",
    )


def compare_approaches(
    source_code: str,
    sink_line: int,
    source_line: int = None,
    method_name: str = None,
) -> Dict:
    """
    Compare different slicing approaches and return all results.

    Useful for experiments: compare backward-only vs chop vs full code.

    Returns dict with:
        - 'backward': ChopResult (backward slice only)
        - 'chop': ChopResult (bidirectional chop, if source_line given)
        - 'full': the original source code
        - 'stats': comparison statistics
    """
    results = {}

    # Backward only
    bw = chop_method(source_code, sink_line, source_line=None,
                     method_name=method_name, auto_source=True)
    results['backward'] = bw

    # Chop (bidirectional)
    if source_line:
        ch = chop_method(source_code, sink_line, source_line=source_line,
                         method_name=method_name)
        results['chop'] = ch

    # Statistics
    results['stats'] = {
        'original_lines': bw.original_count,
        'backward_lines': bw.sliced_count,
        'backward_reduction_pct': bw.compression_pct,
        'chop_lines': results['chop'].sliced_count if 'chop' in results else None,
        'chop_reduction_pct': results['chop'].compression_pct if 'chop' in results else None,
    }

    return results


def _find_node_ids_by_line(pdg: PDG, line: int) -> Set[int]:
    """Find all PDG node IDs at a given source line."""
    return {nid for nid, node in pdg.nodes.items() if node.line == line}


def _find_closest_node_ids(pdg: PDG, line: int) -> Set[int]:
    """Find PDG node IDs closest to a given line number."""
    best = None
    best_dist = float('inf')
    for nid, node in pdg.nodes.items():
        if node.line <= 0:
            continue
        dist = abs(node.line - line)
        if dist < best_dist:
            best_dist = dist
            best = {nid}
        elif dist == best_dist:
            best.add(nid)
    return best or set()


def _backward_slice_with_entry(pdg: PDG, sink_ids: Set[int]) -> Set[int]:
    """Perform backward slice from sink, including ENTRY node results."""
    from .slicing import backward_slice
    result = backward_slice(pdg, sink_ids)
    # Remove EXIT node from results (it's just a marker)
    result.discard(pdg.exit_node_id)
    return result
