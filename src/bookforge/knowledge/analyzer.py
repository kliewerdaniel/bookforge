"""Graph analyzer for discovering concepts and relationships."""

from collections import Counter, defaultdict
from typing import Any

import networkx as nx

from .graph import GraphNode, KnowledgeGraph


class ConceptDiscovery:
    """Discovered concept in the knowledge graph."""

    def __init__(
        self,
        id: str,
        label: str,
        frequency: int,
        centrality: float,
        relationships: list[str],
        properties: dict[str, Any] | None = None,
    ):
        self.id = id
        self.label = label
        self.frequency = frequency
        self.centrality = centrality
        self.relationships = relationships
        self.properties = properties or {}


class RelationshipAnalysis:
    """Analysis of relationships between concepts."""

    def __init__(
        self,
        source: str,
        target: str,
        relationship_type: str,
        weight: float,
        strength: float,
    ):
        self.source = source
        self.target = target
        self.relationship_type = relationship_type
        self.weight = weight
        self.strength = strength


class KnowledgeGap:
    """Identified knowledge gap."""

    def __init__(
        self,
        topic: str,
        description: str,
        importance: str,
        related_concepts: list[str],
    ):
        self.topic = topic
        self.description = description
        self.importance = importance
        self.related_concepts = related_concepts


class SurveyResult:
    """Result of a knowledge graph survey."""

    def __init__(
        self,
        graph_id: str,
        concepts: list[ConceptDiscovery],
        relationships: list[RelationshipAnalysis],
        gaps: list[KnowledgeGap],
        statistics: dict[str, Any],
    ):
        self.graph_id = graph_id
        self.concepts = concepts
        self.relationships = relationships
        self.gaps = gaps
        self.statistics = statistics


class GraphAnalyzer:
    """Analyzes knowledge graphs to discover concepts and relationships."""

    def survey(self, graph: KnowledgeGraph) -> SurveyResult:
        """Perform a complete semantic survey of the knowledge graph.

        Args:
            graph: The knowledge graph to analyze

        Returns:
            Survey results with discovered concepts, relationships, and gaps
        """
        # Convert to NetworkX graph for analysis
        nx_graph = self._to_networkx(graph)

        # Discover concepts
        concepts = self._discover_concepts(graph, nx_graph)

        # Analyze relationships
        relationships = self._analyze_relationships(graph, nx_graph)

        # Identify gaps
        gaps = self._identify_gaps(graph, nx_graph)

        # Calculate statistics
        statistics = self._calculate_statistics(graph, nx_graph)

        return SurveyResult(
            graph_id=graph.id,
            concepts=concepts,
            relationships=relationships,
            gaps=gaps,
            statistics=statistics,
        )

    def _to_networkx(self, graph: KnowledgeGraph) -> nx.DiGraph:
        """Convert to NetworkX graph."""
        nx_graph = nx.DiGraph()

        for node in graph.nodes:
            nx_graph.add_node(
                node.id,
                label=node.label,
                type=node.node_type,
                **node.properties,
            )

        for edge in graph.edges:
            nx_graph.add_edge(
                edge.source,
                edge.target,
                type=edge.edge_type,
                weight=edge.weight,
                **edge.properties,
            )

        return nx_graph

    def _discover_concepts(
        self, graph: KnowledgeGraph, nx_graph: nx.DiGraph
    ) -> list[ConceptDiscovery]:
        """Discover major concepts in the graph."""
        concepts = []

        # Calculate centrality metrics
        try:
            betweenness = nx.betweenness_centrality(nx_graph)
            pagerank = nx.pagerank(nx_graph)
        except Exception:
            betweenness = {node: 0.0 for node in nx_graph.nodes()}
            pagerank = {node: 1.0 / len(nx_graph.nodes()) if nx_graph.nodes() else 0.0 for node in nx_graph.nodes()}

        # Count node occurrences
        node_counts = Counter()
        for edge in graph.edges:
            node_counts[edge.source] += 1
            node_counts[edge.target] += 1

        for node in graph.nodes:
            # Calculate frequency based on connections
            frequency = node_counts.get(node.id, 0)

            # Get centrality scores
            centrality = (betweenness.get(node.id, 0) + pagerank.get(node.id, 0)) / 2

            # Get relationships
            relationships = []
            for edge in graph.edges:
                if edge.source == node.id:
                    relationships.append(f"{edge.edge_type} -> {edge.target}")
                elif edge.target == node.id:
                    relationships.append(f"{edge.edge_type} <- {edge.source}")

            concepts.append(
                ConceptDiscovery(
                    id=node.id,
                    label=node.label,
                    frequency=frequency,
                    centrality=centrality,
                    relationships=relationships,
                    properties=node.properties,
                )
            )

        # Sort by centrality
        concepts.sort(key=lambda c: c.centrality, reverse=True)

        return concepts

    def _analyze_relationships(
        self, graph: KnowledgeGraph, nx_graph: nx.DiGraph
    ) -> list[RelationshipAnalysis]:
        """Analyze relationships between concepts."""
        relationships = []

        for edge in graph.edges:
            # Calculate relationship strength
            source_degree = nx_graph.in_degree(edge.source) + nx_graph.out_degree(edge.source)
            target_degree = nx_graph.in_degree(edge.target) + nx_graph.out_degree(edge.target)

            if source_degree > 0 and target_degree > 0:
                strength = edge.weight * (1 / (source_degree + target_degree))
            else:
                strength = edge.weight

            relationships.append(
                RelationshipAnalysis(
                    source=edge.source,
                    target=edge.target,
                    relationship_type=edge.edge_type,
                    weight=edge.weight,
                    strength=strength,
                )
            )

        # Sort by strength
        relationships.sort(key=lambda r: r.strength, reverse=True)

        return relationships

    def _identify_gaps(
        self, graph: KnowledgeGraph, nx_graph: nx.DiGraph
    ) -> list[KnowledgeGap]:
        """Identify knowledge gaps in the graph."""
        gaps = []

        # Find nodes with few connections
        low_connection_nodes = []
        for node in graph.nodes:
            degree = nx_graph.degree(node.id)
            if degree < 2:
                low_connection_nodes.append(node)

        if low_connection_nodes:
            gaps.append(
                KnowledgeGap(
                    topic="underconnected_concepts",
                    description=f"Found {len(low_connection_nodes)} concepts with fewer than 2 connections",
                    importance="important",
                    related_concepts=[node.id for node in low_connection_nodes],
                )
            )

        # Find potential missing relationships
        for node in graph.nodes:
            neighbors = set()
            for edge in graph.edges:
                if edge.source == node.id:
                    neighbors.add(edge.target)
                elif edge.target == node.id:
                    neighbors.add(edge.source)

            # Check if there are nodes that should be connected
            for other_node in graph.nodes:
                if other_node.id != node.id and other_node.id not in neighbors:
                    # Simple heuristic: nodes with similar types might be related
                    if node.node_type == other_node.node_type:
                        gaps.append(
                            KnowledgeGap(
                                topic=f"potential_connection_{node.id}_{other_node.id}",
                                description=f"Potentially related concepts {node.label} and {other_node.label} are not connected",
                                importance="minor",
                                related_concepts=[node.id, other_node.id],
                            )
                        )

        return gaps

    def _calculate_statistics(
        self, graph: KnowledgeGraph, nx_graph: nx.DiGraph
    ) -> dict[str, Any]:
        """Calculate graph statistics."""
        stats = {
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
            "density": nx.density(nx_graph) if nx_graph.nodes() else 0,
        }

        # Calculate degree statistics
        if nx_graph.nodes():
            degrees = [nx_graph.degree(node) for node in nx_graph.nodes()]
            stats["avg_degree"] = sum(degrees) / len(degrees)
            stats["max_degree"] = max(degrees)
            stats["min_degree"] = min(degrees)

        # Calculate connected components
        try:
            undirected = nx_graph.to_undirected()
            stats["connected_components"] = nx.number_connected_components(undirected)
        except Exception:
            stats["connected_components"] = 1

        # Calculate node type distribution
        node_types = Counter(node.node_type for node in graph.nodes)
        stats["node_types"] = dict(node_types)

        # Calculate edge type distribution
        edge_types = Counter(edge.edge_type for edge in graph.edges)
        stats["edge_types"] = dict(edge_types)

        return stats