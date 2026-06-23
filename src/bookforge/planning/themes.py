"""Theme constructor for grouping concepts into coherent themes."""

from typing import Any
from pydantic import BaseModel, Field

from ..knowledge.graph import KnowledgeGraph
from ..knowledge.analyzer import ConceptDiscovery, SurveyResult


class Theme(BaseModel):
    """A theme grouping related concepts."""

    id: str = Field(..., description="Unique theme identifier")
    name: str = Field(..., description="Theme name")
    description: str = Field(default="", description="Theme description")
    concepts: list[str] = Field(default_factory=list, description="Concept IDs in this theme")
    dependencies: list[str] = Field(default_factory=list, description="Prerequisite theme IDs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Theme metadata")


class ThemeGraph(BaseModel):
    """Graph of themes and their relationships."""

    id: str = Field(..., description="Unique theme graph identifier")
    themes: list[Theme] = Field(default_factory=list, description="Themes")
    relationships: list[dict[str, Any]] = Field(default_factory=list, description="Theme relationships")

    def get_theme(self, theme_id: str) -> Theme | None:
        """Get a theme by ID."""
        for theme in self.themes:
            if theme.id == theme_id:
                return theme
        return None

    def get_dependencies(self, theme_id: str) -> list[Theme]:
        """Get theme dependencies."""
        theme = self.get_theme(theme_id)
        if not theme:
            return []

        deps = []
        for dep_id in theme.dependencies:
            dep_theme = self.get_theme(dep_id)
            if dep_theme:
                deps.append(dep_theme)
        return deps


class ThemeConstructor:
    """Constructs themes from discovered concepts."""

    def construct_themes(
        self,
        survey: SurveyResult,
        graph: KnowledgeGraph,
        max_themes: int = 10,
    ) -> ThemeGraph:
        """Construct themes from survey results.

        Args:
            survey: Survey results with discovered concepts
            graph: Original knowledge graph
            max_themes: Maximum number of themes to create

        Returns:
            Theme graph with constructed themes
        """
        # Group concepts by similarity
        concept_groups = self._group_concepts(survey.concepts, graph)

        # Create themes from groups
        themes = self._create_themes(concept_groups, survey)

        # Limit to max_themes
        themes = themes[:max_themes]

        # Establish theme dependencies
        themes = self._establish_dependencies(themes)

        return ThemeGraph(
            id=f"themes-{survey.graph_id}",
            themes=themes,
            relationships=self._create_relationships(themes),
        )

    def _group_concepts(
        self,
        concepts: list[ConceptDiscovery],
        graph: KnowledgeGraph,
    ) -> list[list[ConceptDiscovery]]:
        """Group concepts by similarity."""
        if not concepts:
            return []

        # Simple grouping by node type and connectivity
        groups: dict[str, list[ConceptDiscovery]] = {}

        for concept in concepts:
            # Get node from graph
            node = graph.get_node(concept.id)
            if not node:
                continue

            # Group by node type
            group_key = node.node_type
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(concept)

        # Further split large groups by connectivity
        final_groups = []
        for group_concepts in groups.values():
            if len(group_concepts) > 5:
                # Split by centrality
                high_central = [c for c in group_concepts if c.centrality > 0.5]
                low_central = [c for c in group_concepts if c.centrality <= 0.5]

                if high_central:
                    final_groups.append(high_central)
                if low_central:
                    final_groups.append(low_central)
            else:
                final_groups.append(group_concepts)

        return final_groups

    def _create_themes(
        self,
        concept_groups: list[list[ConceptDiscovery]],
        survey: SurveyResult,
    ) -> list[Theme]:
        """Create themes from concept groups."""
        themes = []

        for i, group in enumerate(concept_groups):
            if not group:
                continue

            # Calculate theme importance
            avg_centrality = sum(c.centrality for c in group) / len(group)

            # Create theme name from most central concept
            main_concept = max(group, key=lambda c: c.centrality)

            # Generate description
            concept_labels = [c.label for c in group[:5]]
            description = f"Theme covering: {', '.join(concept_labels)}"
            if len(group) > 5:
                description += f" and {len(group) - 5} more concepts"

            theme = Theme(
                id=f"theme-{i}",
                name=main_concept.label,
                description=description,
                concepts=[c.id for c in group],
                metadata={
                    "importance": avg_centrality,
                    "concept_count": len(group),
                },
            )
            themes.append(theme)

        # Sort by importance
        themes.sort(key=lambda t: t.metadata.get("importance", 0), reverse=True)

        return themes

    def _establish_dependencies(self, themes: list[Theme]) -> list[Theme]:
        """Establish dependencies between themes."""
        # Simple heuristic: themes with lower importance depend on higher importance themes
        for i, theme in enumerate(themes):
            if i > 0:
                # Depend on the previous theme
                theme.dependencies.append(themes[i - 1].id)

        return themes

    def _create_relationships(self, themes: list[Theme]) -> list[dict[str, Any]]:
        """Create relationships between themes."""
        relationships = []

        for theme in themes:
            for dep_id in theme.dependencies:
                relationships.append(
                    {
                        "source": dep_id,
                        "target": theme.id,
                        "type": "depends_on",
                    }
                )

        return relationships