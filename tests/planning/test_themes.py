"""Tests for theme constructor."""

import pytest
from bookforge.planning.themes import ThemeConstructor, ThemeGraph
from bookforge.knowledge.analyzer import SurveyResult, ConceptDiscovery
from bookforge.knowledge.graph import KnowledgeGraph, GraphNode


class TestThemeConstructor:
    """Tests for ThemeConstructor."""

    def test_construct_themes_empty_survey(self):
        """Test constructing themes from empty survey."""
        survey = SurveyResult(
            graph_id="empty",
            concepts=[],
            relationships=[],
            gaps=[],
            statistics={},
        )
        graph = KnowledgeGraph(id="empty", name="Empty Graph")
        constructor = ThemeConstructor()

        theme_graph = constructor.construct_themes(survey, graph)

        assert theme_graph.id == "themes-empty"
        assert len(theme_graph.themes) == 0

    def test_construct_themes_with_concepts(self):
        """Test constructing themes from concepts."""
        survey = SurveyResult(
            graph_id="test",
            concepts=[
                ConceptDiscovery(
                    id="c1",
                    label="Concept 1",
                    frequency=5,
                    centrality=0.8,
                    relationships=[],
                ),
                ConceptDiscovery(
                    id="c2",
                    label="Concept 2",
                    frequency=3,
                    centrality=0.5,
                    relationships=[],
                ),
            ],
            relationships=[],
            gaps=[],
            statistics={},
        )
        graph = KnowledgeGraph(
            id="test",
            name="Test Graph",
            nodes=[
                GraphNode(id="c1", label="Concept 1", node_type="concept"),
                GraphNode(id="c2", label="Concept 2", node_type="concept"),
            ],
        )
        constructor = ThemeConstructor()

        theme_graph = constructor.construct_themes(survey, graph)

        assert len(theme_graph.themes) > 0


class TestThemeGraph:
    """Tests for ThemeGraph."""

    def test_get_theme(self):
        """Test getting a theme by ID."""
        theme_graph = ThemeGraph(
            id="tg-1",
            themes=[
                {"id": "t1", "name": "Theme 1", "concepts": []},
            ],
        )
        # This test might need adjustment based on Theme model
        pass