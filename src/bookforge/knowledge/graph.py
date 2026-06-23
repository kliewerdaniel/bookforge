"""Knowledge graph data models."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """A node in the knowledge graph."""

    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Human-readable node label")
    node_type: str = Field(..., description="Node type (concept, entity, topic, etc.)")
    properties: dict[str, Any] = Field(default_factory=dict, description="Node properties")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class GraphEdge(BaseModel):
    """An edge in the knowledge graph."""

    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    edge_type: str = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, description="Relationship weight")
    properties: dict[str, Any] = Field(default_factory=dict, description="Edge properties")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class KnowledgeGraph(BaseModel):
    """A knowledge graph containing nodes and edges."""

    id: str = Field(..., description="Unique graph identifier")
    name: str = Field(..., description="Graph name")
    description: str = Field(default="", description="Graph description")
    nodes: list[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: list[GraphEdge] = Field(default_factory=list, description="Graph edges")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Graph metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    def get_node(self, node_id: str) -> GraphNode | None:
        """Get a node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        """Get neighboring nodes."""
        neighbors = []
        for edge in self.edges:
            if direction in ("out", "both") and edge.source == node_id:
                target_node = self.get_node(edge.target)
                if target_node:
                    neighbors.append(target_node)
            if direction in ("in", "both") and edge.target == node_id:
                source_node = self.get_node(edge.source)
                if source_node:
                    neighbors.append(source_node)
        return neighbors

    def get_edges_for_node(self, node_id: str, direction: str = "both") -> list[GraphEdge]:
        """Get edges connected to a node."""
        edges = []
        for edge in self.edges:
            if direction in ("out", "both") and edge.source == node_id:
                edges.append(edge)
            if direction in ("in", "both") and edge.target == node_id:
                edges.append(edge)
        return edges

    @property
    def node_count(self) -> int:
        """Get the number of nodes."""
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        """Get the number of edges."""
        return len(self.edges)