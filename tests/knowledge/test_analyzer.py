"""Tests for graph analyzer."""

import pytest
from bookforge.knowledge.graph import KnowledgeGraph, GraphNode, GraphEdge
from bookforge.knowledge.analyzer import GraphAnalyzer


class TestGraphAnalyzer:
    """Tests for GraphAnalyzer."""

    def test_survey_empty_graph(self):
        """Test surveying an empty graph."""
        graph = KnowledgeGraph(id="empty", name="Empty Graph")
        analyzer = GraphAnalyzer()

        result = analyzer.survey(graph)

        assert result.graph_id == "empty"
        assert len(result.concepts) == 0
        assert len(result.relationships) == 0

    def test_survey_simple_graph(self):
        """Test surveying a simple graph."""
        graph = KnowledgeGraph(
            id="simple",
            name="Simple Graph",
            nodes=[
                GraphNode(id="n1", label="Concept 1", node_type="concept"),
                GraphNode(id="n2", label="Concept 2", node_type="concept"),
            ],
            edges=[
                GraphEdge(id="e1", source="n1", target="n2", edge_type="related_to"),
            ],
        )
        analyzer = GraphAnalyzer()

        result = analyzer.survey(graph)

        assert result.graph_id == "simple"
        assert len(result.concepts) == 2
        assert len(result.relationships) == 1

    def test_calculate_statistics(self):
        """Test calculating graph statistics."""
        graph = KnowledgeGraph(
            id="stats",
            name="Stats Graph",
            nodes=[
                GraphNode(id="n1", label="Node 1", node_type="concept"),
                GraphNode(id="n2", label="Node 2", node_type="concept"),
                GraphNode(id="n3", label="Node 3", node_type="topic"),
            ],
            edges=[
                GraphEdge(id="e1", source="n1", target="n2", edge_type="related_to"),
                GraphEdge(id="e2", source="n2", target="n3", edge_type="contains"),
            ],
        )
        analyzer = GraphAnalyzer()

        result = analyzer.survey(graph)

        assert result.statistics["node_count"] == 3
        assert result.statistics["edge_count"] == 2
        assert "concept" in result.statistics["node_types"]
        assert "topic" in result.statistics["node_types"]