"""
Chop4LLM: Program Slicing meets Large Language Models.

Converts source code into Program Dependence Graphs, applies
bidirectional slicing (Chop) to isolate bug-relevant code,
and formats results into structured LLM prompts.

Core components:
- pdg: PDG construction from AST (def-use + control dep)
- slicing: Forward, backward, and Chop algorithms on PDG
- formatter: Template-based LLM prompt formatting
- api: Clean public API (borrowed from GitIngest style)
"""

from .api import chop_method, compare_approaches, ChopResult
from .models import PDG, PDGNode, PDGEdge, EdgeType, NodeType
from .slicing import forward_slice, backward_slice, chop

__version__ = "0.1.0"
__all__ = [
    "chop_method",
    "compare_approaches",
    "ChopResult",
    "PDG",
    "PDGNode",
    "PDGEdge",
    "EdgeType",
    "NodeType",
    "forward_slice",
    "backward_slice",
    "chop",
]
