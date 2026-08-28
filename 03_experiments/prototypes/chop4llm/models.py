"""
Chop4LLM Data Models

PDG node/edge representation and slice result types.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class EdgeType(str, Enum):
    DATA_DEP = "data_dep"       # def-use chain
    CONTROL_DEP = "control_dep" # branch condition → controlled statement


class NodeType(str, Enum):
    ASSIGNMENT = "assignment"
    METHOD_CALL = "method_call"
    CONDITION = "condition"     # if / while / for condition
    RETURN = "return"
    DECLARATION = "declaration"
    ENTRY = "entry"             # method entry (formal parameters)
    EXIT = "exit"               # method exit
    OTHER = "other"


@dataclass
class PDGNode:
    """A single node in the Program Dependence Graph."""
    id: int
    line: int                   # source line number (1-based)
    end_line: int = 0           # end line for multi-line statements
    code: str = ""              # source code text
    node_type: NodeType = NodeType.OTHER
    defined_vars: Set[str] = field(default_factory=set)
    used_vars: Set[str] = field(default_factory=set)

    def __hash__(self):
        return hash(self.id)


@dataclass
class PDGEdge:
    """An edge in the Program Dependence Graph."""
    source: int   # PDGNode.id
    target: int   # PDGNode.id
    edge_type: EdgeType
    variable: Optional[str] = None


@dataclass
class PDG:
    """
    Program Dependence Graph for a single method.

    Combines data dependence edges and control dependence edges
    into a single graph. Also stores the original source code.
    """
    method_name: str = ""
    source_code: str = ""
    nodes: Dict[int, PDGNode] = field(default_factory=dict)
    edges: List[PDGEdge] = field(default_factory=list)
    entry_node_id: int = -1
    exit_node_id: int = -1

    # Cached adjacency for fast traversal
    _forward_adj: Dict[int, List[int]] = field(default_factory=dict, repr=False)
    _backward_adj: Dict[int, List[int]] = field(default_factory=dict, repr=False)

    def add_node(self, node: PDGNode) -> int:
        self.nodes[node.id] = node
        return node.id

    def add_edge(self, source: int, target: int, edge_type: EdgeType, variable: str = None):
        self.edges.append(PDGEdge(source, target, edge_type, variable))

    def _build_adjacency(self):
        """Build forward and backward adjacency lists."""
        self._forward_adj.clear()
        self._backward_adj.clear()
        for nid in self.nodes:
            self._forward_adj[nid] = []
            self._backward_adj[nid] = []
        for edge in self.edges:
            self._forward_adj[edge.source].append(edge.target)
            self._backward_adj[edge.target].append(edge.source)

    def successors(self, node_id: int) -> List[int]:
        if not self._forward_adj:
            self._build_adjacency()
        return self._forward_adj.get(node_id, [])

    def predecessors(self, node_id: int) -> List[int]:
        if not self._backward_adj:
            self._build_adjacency()
        return self._backward_adj.get(node_id, [])

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)


@dataclass
class SliceResult:
    """Result of a slicing operation."""
    method_name: str = ""
    original_code: str = ""
    sliced_lines: List[int] = field(default_factory=list)
    sliced_code: str = ""
    slice_nodes: List[PDGNode] = field(default_factory=list)
    original_lines: int = 0
    sliced_line_count: int = 0
    compression_ratio: float = 0.0
    dependency_chains: List[List[PDGNode]] = field(default_factory=list)

    @property
    def compression_pct(self) -> float:
        """Percentage of original code removed."""
        if self.original_lines == 0:
            return 0.0
        return (1 - self.sliced_line_count / self.original_lines) * 100
