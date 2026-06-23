"""Chapter generator for creating chapter content."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from ..planning.blueprint import ChapterSpec, IllustrationSpec
from ..research.evidence import EvidenceMap


class GeneratedParagraph(BaseModel):
    """A generated paragraph with evidence."""

    id: str = Field(..., description="Unique paragraph identifier")
    content: str = Field(..., description="Paragraph content")
    citations: list[str] = Field(default_factory=list, description="Inline citations")
    evidence_map: EvidenceMap | None = Field(default=None, description="Evidence map for this paragraph")
    order: int = Field(default=0, description="Paragraph order")


class GeneratedSection(BaseModel):
    """A generated section containing paragraphs."""

    id: str = Field(..., description="Unique section identifier")
    title: str = Field(..., description="Section title")
    paragraphs: list[GeneratedParagraph] = Field(default_factory=list, description="Section paragraphs")
    order: int = Field(default=0, description="Section order")


class GeneratedChapter(BaseModel):
    """A fully generated chapter."""

    id: str = Field(..., description="Unique chapter identifier")
    title: str = Field(..., description="Chapter title")
    content: str = Field(default="", description="Full chapter content in markdown")
    sections: list[GeneratedSection] = Field(default_factory=list, description="Chapter sections")
    word_count: int = Field(default=0, description="Chapter word count")
    citations: list[str] = Field(default_factory=list, description="All citations in chapter")
    illustration_specs: list[IllustrationSpec] = Field(default_factory=list, description="Illustration specifications")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Chapter metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")

    def calculate_word_count(self) -> int:
        """Calculate word count from content."""
        if self.content:
            self.word_count = len(self.content.split())
        else:
            # Calculate from sections
            total = 0
            for section in self.sections:
                for paragraph in section.paragraphs:
                    total += len(paragraph.content.split())
            self.word_count = total
        return self.word_count


class ChapterGenerator:
    """Generates chapter content from specifications."""

    def __init__(self):
        self.paragraph_templates = {
            "introduction": "This chapter introduces {topic}...",
            "definition": "{concept} refers to...",
            "explanation": "To understand {concept}, consider...",
            "example": "For example, {example}...",
            "conclusion": "In summary, {summary}...",
        }

    def generate_chapter(
        self,
        spec: ChapterSpec,
        evidence_maps: list[EvidenceMap] | None = None,
    ) -> GeneratedChapter:
        """Generate a chapter from its specification.

        Args:
            spec: Chapter specification
            evidence_maps: Evidence maps for the chapter

        Returns:
            Generated chapter
        """
        sections = []
        all_citations = []

        # Generate introduction section
        intro_section = self._generate_introduction(spec)
        sections.append(intro_section)

        # Generate main content sections based on objectives
        for i, objective in enumerate(spec.objectives):
            section = self._generate_section(spec, objective.description, i + 1)
            sections.append(section)

        # Generate conclusion section
        conclusion_section = self._generate_conclusion(spec)
        sections.append(conclusion_section)

        # Compile full content
        content = self._compile_content(spec.title, sections)

        # Collect all citations
        for section in sections:
            for paragraph in section.paragraphs:
                all_citations.extend(paragraph.citations)

        chapter = GeneratedChapter(
            id=spec.id,
            title=spec.title,
            content=content,
            sections=sections,
            citations=list(set(all_citations)),
            illustration_specs=spec.illustration_specs,
            metadata={
                "theme_id": spec.theme_id,
                "objectives_count": len(spec.objectives),
                "evidence_sources": spec.evidence_sources,
            },
        )
        chapter.calculate_word_count()

        return chapter

    def _generate_introduction(self, spec: ChapterSpec) -> GeneratedSection:
        """Generate introduction section."""
        paragraphs = []

        # Generate introductory paragraph
        intro_content = f"## Introduction\n\nThis chapter explores {spec.title}. "
        if spec.objectives:
            obj_descriptions = [obj.description for obj in spec.objectives[:3]]
            intro_content += f"By the end of this chapter, you will be able to: {', '.join(obj_descriptions)}."

        paragraphs.append(
            GeneratedParagraph(
                id=f"{spec.id}-intro-0",
                content=intro_content,
                citations=[],
                order=0,
            )
        )

        return GeneratedSection(
            id=f"{spec.id}-intro",
            title="Introduction",
            paragraphs=paragraphs,
            order=0,
        )

    def _generate_section(
        self, spec: ChapterSpec, topic: str, section_num: int
    ) -> GeneratedSection:
        """Generate a content section."""
        paragraphs = []

        # Generate section heading
        section_title = f"Section {section_num}: {topic}"

        # Generate content paragraph
        content = f"This section covers {topic}. "
        content += f"The concept is fundamental to understanding {spec.title}."

        paragraphs.append(
            GeneratedParagraph(
                id=f"{spec.id}-s{section_num}-0",
                content=content,
                citations=[f"ref-{spec.id}-{section_num}"],
                order=0,
            )
        )

        return GeneratedSection(
            id=f"{spec.id}-s{section_num}",
            title=section_title,
            paragraphs=paragraphs,
            order=section_num,
        )

    def _generate_conclusion(self, spec: ChapterSpec) -> GeneratedSection:
        """Generate conclusion section."""
        paragraphs = []

        # Generate conclusion paragraph
        content = f"In this chapter, we explored {spec.title}. "
        content += "The concepts covered provide a foundation for understanding the broader topic."

        paragraphs.append(
            GeneratedParagraph(
                id=f"{spec.id}-conclusion-0",
                content=content,
                citations=[],
                order=0,
            )
        )

        return GeneratedSection(
            id=f"{spec.id}-conclusion",
            title="Conclusion",
            paragraphs=paragraphs,
            order=999,
        )

    def _compile_content(self, title: str, sections: list[GeneratedSection]) -> str:
        """Compile sections into full chapter content."""
        lines = [f"# {title}", ""]

        for section in sections:
            lines.append(section.title)
            lines.append("")
            for paragraph in section.paragraphs:
                lines.append(paragraph.content)
                lines.append("")

        return "\n".join(lines)