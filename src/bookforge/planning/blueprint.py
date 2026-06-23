"""Blueprint generator for creating book structure."""

from typing import Any
from pydantic import BaseModel, Field

from .themes import Theme, ThemeGraph


class LearningObjective(BaseModel):
    """A learning objective for a chapter or section."""

    id: str = Field(..., description="Unique objective identifier")
    description: str = Field(..., description="What the reader will learn")
    level: str = Field(default="understand", description="Bloom's taxonomy level")


class IllustrationSpec(BaseModel):
    """Specification for a technical illustration."""

    id: str = Field(..., description="Unique illustration identifier")
    purpose: str = Field(..., description="Illustration purpose")
    concepts: list[str] = Field(default_factory=list, description="Concepts to illustrate")
    entities: list[str] = Field(default_factory=list, description="Required entities")
    layout: str = Field(default="diagram", description="Layout type")
    labels: dict[str, str] = Field(default_factory=dict, description="Entity labels")
    caption: str = Field(default="", description="Illustration caption")
    references: list[str] = Field(default_factory=list, description="Supporting references")


class ChapterSpec(BaseModel):
    """Specification for a book chapter."""

    id: str = Field(..., description="Unique chapter identifier")
    title: str = Field(..., description="Chapter title")
    theme_id: str = Field(..., description="Associated theme ID")
    objectives: list[LearningObjective] = Field(default_factory=list, description="Learning objectives")
    evidence_sources: list[str] = Field(default_factory=list, description="Required evidence sources")
    illustration_specs: list[IllustrationSpec] = Field(default_factory=list, description="Illustration specifications")
    word_count_target: int = Field(default=5000, description="Target word count")
    order: int = Field(default=0, description="Chapter order")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Chapter metadata")


class BookPart(BaseModel):
    """A high-level division of the book."""

    id: str = Field(..., description="Unique part identifier")
    title: str = Field(..., description="Part title")
    description: str = Field(default="", description="Part description")
    chapters: list[str] = Field(default_factory=list, description="Chapter IDs in this part")
    theme_ids: list[str] = Field(default_factory=list, description="Associated theme IDs")


class BookBlueprint(BaseModel):
    """Complete book blueprint."""

    id: str = Field(..., description="Unique blueprint identifier")
    title: str = Field(..., description="Book title")
    description: str = Field(default="", description="Book description")
    parts: list[BookPart] = Field(default_factory=list, description="Book parts")
    chapters: list[ChapterSpec] = Field(default_factory=list, description="All chapters")
    learning_objectives: list[LearningObjective] = Field(default_factory=list, description="Overall learning objectives")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Blueprint metadata")

    def get_chapter(self, chapter_id: str) -> ChapterSpec | None:
        """Get a chapter by ID."""
        for chapter in self.chapters:
            if chapter.id == chapter_id:
                return chapter
        return None

    def get_part(self, part_id: str) -> BookPart | None:
        """Get a part by ID."""
        for part in self.parts:
            if part.id == part_id:
                return part
        return None

    @property
    def total_word_count(self) -> int:
        """Get total target word count."""
        return sum(chapter.word_count_target for chapter in self.chapters)


class BlueprintGenerator:
    """Generates book blueprints from themes."""

    def generate(
        self,
        theme_graph: ThemeGraph,
        title: str = "Untitled Book",
        description: str = "",
    ) -> BookBlueprint:
        """Generate a book blueprint from themes.

        Args:
            theme_graph: Theme graph with constructed themes
            title: Book title
            description: Book description

        Returns:
            Complete book blueprint
        """
        # Create parts from themes
        parts = self._create_parts(theme_graph)

        # Create chapters from themes
        chapters = self._create_chapters(theme_graph)

        # Assign chapters to parts
        parts = self._assign_chapters_to_parts(parts, chapters)

        # Create overall learning objectives
        objectives = self._create_objectives(chapters)

        return BookBlueprint(
            id=f"blueprint-{theme_graph.id}",
            title=title,
            description=description,
            parts=parts,
            chapters=chapters,
            learning_objectives=objectives,
            metadata={
                "theme_count": len(theme_graph.themes),
                "chapter_count": len(chapters),
                "part_count": len(parts),
            },
        )

    def _create_parts(self, theme_graph: ThemeGraph) -> list[BookPart]:
        """Create book parts from themes."""
        parts = []

        # Group themes into parts (simple: each theme becomes a part)
        for i, theme in enumerate(theme_graph.themes):
            part = BookPart(
                id=f"part-{i}",
                title=theme.name,
                description=theme.description,
                theme_ids=[theme.id],
            )
            parts.append(part)

        return parts

    def _create_chapters(self, theme_graph: ThemeGraph) -> list[ChapterSpec]:
        """Create chapters from themes."""
        chapters = []

        for i, theme in enumerate(theme_graph.themes):
            # Create a chapter for each theme
            chapter = ChapterSpec(
                id=f"chapter-{i}",
                title=theme.name,
                theme_id=theme.id,
                objectives=[
                    LearningObjective(
                        id=f"obj-{i}-0",
                        description=f"Understand {theme.name}",
                        level="understand",
                    )
                ],
                evidence_sources=theme.concepts,
                word_count_target=5000,
                order=i,
                metadata={
                    "concept_count": len(theme.concepts),
                    "importance": theme.metadata.get("importance", 0),
                },
            )
            chapters.append(chapter)

        return chapters

    def _assign_chapters_to_parts(
        self, parts: list[BookPart], chapters: list[ChapterSpec]
    ) -> list[BookPart]:
        """Assign chapters to parts."""
        for part in parts:
            # Find chapters for this part's themes
            part_chapters = [
                chapter.id
                for chapter in chapters
                if chapter.theme_id in part.theme_ids
            ]
            part.chapters = part_chapters

        return parts

    def _create_objectives(self, chapters: list[ChapterSpec]) -> list[LearningObjective]:
        """Create overall learning objectives."""
        objectives = []

        for i, chapter in enumerate(chapters):
            objectives.extend(chapter.objectives)

        return objectives