"""Gap analyzer for identifying knowledge gaps."""

from typing import Any
from pydantic import BaseModel, Field

from ..knowledge.graph import KnowledgeGraph


class KnowledgeGap(BaseModel):
    """A knowledge gap identified in the graph."""

    id: str = Field(..., description="Unique gap identifier")
    topic: str = Field(..., description="Gap topic")
    description: str = Field(..., description="Gap description")
    importance: str = Field(..., description="Gap importance (critical, important, minor)")
    related_concepts: list[str] = Field(default_factory=list, description="Related concept IDs")
    research_sources: list[str] = Field(default_factory=list, description="Potential research sources")
    resolution_strategy: str = Field(default="", description="How to address the gap")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GapAnalysisResult:
    """Result of gap analysis."""

    def __init__(
        self,
        graph_id: str,
        gaps: list[KnowledgeGap],
        coverage_score: float,
        recommendations: list[str],
    ):
        self.graph_id = graph_id
        self.gaps = gaps
        self.coverage_score = coverage_score
        self.recommendations = recommendations


class GapAnalyzer:
    """Analyzes knowledge graphs to identify gaps."""

    def analyze(self, graph: KnowledgeGraph) -> GapAnalysisResult:
        """Analyze a knowledge graph to identify gaps.

        Args:
            graph: The knowledge graph to analyze

        Returns:
            Gap analysis results
        """
        gaps = []

        # Find isolated nodes
        isolated_gaps = self._find_isolated_nodes(graph)
        gaps.extend(isolated_gaps)

        # Find missing relationships
        relationship_gaps = self._find_missing_relationships(graph)
        gaps.extend(relationship_gaps)

        # Find underrepresented topics
        topic_gaps = self._find_underrepresented_topics(graph)
        gaps.extend(topic_gaps)

        # Calculate coverage score
        coverage_score = self._calculate_coverage_score(graph, gaps)

        # Generate recommendations
        recommendations = self._generate_recommendations(gaps)

        return GapAnalysisResult(
            graph_id=graph.id,
            gaps=gaps,
            coverage_score=coverage_score,
            recommendations=recommendations,
        )

    def _find_isolated_nodes(self, graph: KnowledgeGraph) -> list[KnowledgeGap]:
        """Find nodes with no or few connections."""
        gaps = []

        # Count connections for each node
        connection_counts: dict[str, int] = {}
        for node in graph.nodes:
            connection_counts[node.id] = 0

        for edge in graph.edges:
            if edge.source in connection_counts:
                connection_counts[edge.source] += 1
            if edge.target in connection_counts:
                connection_counts[edge.target] += 1

        # Find isolated nodes (0 connections)
        isolated = [node_id for node_id, count in connection_counts.items() if count == 0]
        if isolated:
            gaps.append(
                KnowledgeGap(
                    id="gap-isolated",
                    topic="isolated_concepts",
                    description=f"Found {len(isolated)} concepts with no connections",
                    importance="important",
                    related_concepts=isolated,
                    resolution_strategy="Add relationships between isolated concepts and the rest of the graph",
                )
            )

        # Find poorly connected nodes (1 connection)
        poorly_connected = [
            node_id for node_id, count in connection_counts.items() if count == 1
        ]
        if poorly_connected:
            gaps.append(
                KnowledgeGap(
                    id="gap-poorly-connected",
                    topic="poorly_connected_concepts",
                    description=f"Found {len(poorly_connected)} concepts with only 1 connection",
                    importance="minor",
                    related_concepts=poorly_connected,
                    resolution_strategy="Add more relationships to integrate these concepts better",
                )
            )

        return gaps

    def _find_missing_relationships(self, graph: KnowledgeGraph) -> list[KnowledgeGap]:
        """Find potential missing relationships between concepts."""
        gaps = []

        # Group nodes by type
        nodes_by_type: dict[str, list[str]] = {}
        for node in graph.nodes:
            if node.node_type not in nodes_by_type:
                nodes_by_type[node.node_type] = []
            nodes_by_type[node.node_type].append(node.id)

        # Check for missing relationships within types
        for node_type, node_ids in nodes_by_type.items():
            if len(node_ids) > 1:
                # Check if all nodes of this type are connected
                connected_pairs = set()
                for edge in graph.edges:
                    if edge.source in node_ids and edge.target in node_ids:
                        pair = tuple(sorted([edge.source, edge.target]))
                        connected_pairs.add(pair)

                expected_pairs = len(node_ids) * (len(node_ids) - 1) / 2
                if len(connected_pairs) < expected_pairs:
                    gaps.append(
                        KnowledgeGap(
                            id=f"gap-missing-{node_type}",
                            topic=f"missing_{node_type}_relationships",
                            description=f"Some {node_type} concepts are not connected to each other",
                            importance="minor",
                            related_concepts=node_ids,
                            resolution_strategy=f"Add relationships between {node_type} concepts",
                        )
                    )

        return gaps

    def _find_underrepresented_topics(self, graph: KnowledgeGraph) -> list[KnowledgeGap]:
        """Find topics with insufficient coverage."""
        gaps = []

        # Count nodes by type
        type_counts: dict[str, int] = {}
        for node in graph.nodes:
            type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1

        # Find types with very few nodes
        for node_type, count in type_counts.items():
            if count < 3 and node_type not in ("specification", "test_case"):
                gaps.append(
                    KnowledgeGap(
                        id=f"gap-underrepresented-{node_type}",
                        topic=f"underrepresented_{node_type}",
                        description=f"Only {count} {node_type} concepts found",
                        importance="important",
                        related_concepts=[
                            node.id for node in graph.nodes if node.node_type == node_type
                        ],
                        resolution_strategy=f"Add more {node_type} concepts to improve coverage",
                    )
                )

        return gaps

    def _calculate_coverage_score(
        self, graph: KnowledgeGraph, gaps: list[KnowledgeGap]
    ) -> float:
        """Calculate overall coverage score."""
        if not graph.nodes:
            return 0.0

        # Start with perfect score and deduct for gaps
        score = 1.0

        for gap in gaps:
            if gap.importance == "critical":
                score -= 0.2
            elif gap.importance == "important":
                score -= 0.1
            elif gap.importance == "minor":
                score -= 0.05

        return max(0.0, min(1.0, score))

    def _generate_recommendations(self, gaps: list[KnowledgeGap]) -> list[str]:
        """Generate recommendations for addressing gaps."""
        recommendations = []

        for gap in gaps:
            if gap.importance in ("critical", "important"):
                recommendations.append(
                    f"Address {gap.topic}: {gap.resolution_strategy}"
                )

        return recommendations