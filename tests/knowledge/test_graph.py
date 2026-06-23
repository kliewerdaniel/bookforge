"""Tests for knowledge graph module."""

import pytest
from bookforge.knowledge.graph import KnowledgeGraph, GraphNode, GraphEdge


class TestGraphNode:
    """Tests for GraphNode."""

    def test_create_node(self):
        """Test creating a node."""
        node = GraphNode(
            id="node-1",
            label="Test Node",
            node_type="concept",
        )
        assert node.id == "node-1"
        assert node.label == "Test Node"
        assert node.node_type == "concept"

    def test_node_with_properties(self):
        """Test creating a node with properties."""
        node = GraphNode(
            id="node-1",
            label="Test Node",
            node_type="concept",
            properties={"key": "value"},
        )
        assert node.properties == {"key": "value"}


class TestGraphEdge:
    """Tests for GraphEdge."""

    def test_create_edge(self):
        """Test creating an edge."""
        edge = GraphEdge(
            id="edge-1",
            source="node-1",
            target="node-2",
            edge_type="related_to",
        )
        assert edge.id == "edge-1"
        assert edge.source == "node-1"
        assert edge.target == "node-2"
        assert edge.edge_type == "related_to"

    def test_edge_with_weight(self):
        """Test creating an edge with weight."""
        edge = GraphEdge(
            id="edge-1",
            source="node-1",
            target="node-2",
            edge_type="related_to",
            weight=0.8,
        )
        assert edge.weight == 0.8


class TestKnowledgeGraph:
    """Tests for KnowledgeGraph."""

    def test_create_graph(self):
        """Test creating a knowledge graph."""
        graph = KnowledgeGraph(
            id="graph-1",
            name="Test Graph",
        )
        assert graph.id == "graph-1"
        assert graph.name == "Test Graph"
        assert graph.node_count == 0
        assert graph.edge_count == 0

    def test_add_nodes(self):
        """Test adding nodes to graph."""
        graph = KnowledgeGraph(id="graph-1", name="Test Graph")
        graph.nodes.append(GraphNode(id="n1", label="Node 1", node_type="concept"))
        graph.nodes.append(GraphNode(id="n2", label="Node 2", node_type="concept"))
        assert graph.node_count == 2

    def test_add_edges(self):
        """Test adding edges to graph."""
        graph = KnowledgeGraph(id="graph-1", name="Test Graph")
        graph.edges.append(
            GraphEdge(id="e1", source="n1", target="n2", edge_type="related_to")
        )
        assert graph.edge_count == 1

    def test_get_node(self):
        """Test getting a node by ID."""
        graph = KnowledgeGraph(id="graph-1", name="Test Graph")
        graph.nodes.append(GraphNode(id="n1", label="Node 1", node_type="concept"))
        node = graph.get_node("n1")
        assert node is not None
        assert node.id == "n1"

    def test_get_node_not_found(self):
        """Test getting a non-existent node."""
        graph = KnowledgeGraph(id="graph-1", name="Test Graph")
        node = graph.get_node("nonexistent")
        assert node is None

    def test_get_neighbors(self):
        """Test getting neighboring nodes."""
        graph = KnowledgeGraph(id="graph-1", name="Test Graph")
        graph.nodes.append(GraphNode(id="n1", label="Node 1", node_type="concept"))
        graph.nodes.append(GraphNode(id="n2", label="Node 2", node_type="concept"))
        graph.edges.append(
            GraphEdge(id="e1", source="n1", target="n2", edge_type="related_to")
        )
        neighbors = graph.get_neighbors("n1", direction="out")
        assert len(neighbors) == 1
        assert neighbors[0].id == "n2"