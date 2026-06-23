"""Evidence-backed writer for generating content with provenance."""

from typing import Any

from ..research.evidence import EvidenceCollector, EvidenceMap, EvidenceItem
from .generator import GeneratedParagraph, GeneratedSection, GeneratedChapter
from ..planning.blueprint import ChapterSpec


class EvidenceBackedWriter:
    """Generates content with evidence backing and provenance tracking."""

    def __init__(self, evidence_collector: EvidenceCollector):
        self.evidence_collector = evidence_collector

    def write_with_evidence(
        self,
        spec: ChapterSpec,
        claims: list[str] | None = None,
    ) -> GeneratedChapter:
        """Write a chapter with evidence backing.

        Args:
            spec: Chapter specification
            claims: Claims to find evidence for (auto-generated if not provided)

        Returns:
            Chapter with evidence maps
        """
        # Generate claims if not provided
        if not claims:
            claims = self._generate_claims(spec)

        # Collect evidence for each claim
        evidence_items = []
        for claim in claims:
            evidence = self.evidence_collector.collect_evidence(claim)
            evidence_items.append(evidence)

        # Generate content with evidence
        sections = self._generate_sections_with_evidence(spec, evidence_items)

        # Compile content
        content = self._compile_content(spec.title, sections)

        # Create chapter
        chapter = GeneratedChapter(
            id=spec.id,
            title=spec.title,
            content=content,
            sections=sections,
            metadata={
                "evidence_count": len(evidence_items),
                "avg_confidence": self._calculate_avg_confidence(evidence_items),
            },
        )
        chapter.calculate_word_count()

        return chapter

    def _generate_claims(self, spec: ChapterSpec) -> list[str]:
        """Generate claims from chapter specification."""
        claims = []

        # Generate claims from objectives
        for objective in spec.objectives:
            claims.append(objective.description)

        # Generate claims from evidence sources
        for source in spec.evidence_sources:
            claims.append(f"Concept {source} is important for understanding {spec.title}")

        return claims

    def _generate_sections_with_evidence(
        self,
        spec: ChapterSpec,
        evidence_items: list[EvidenceItem],
    ) -> list[GeneratedSection]:
        """Generate sections with evidence backing."""
        sections = []

        # Create introduction section
        intro_section = self._create_introduction_section(spec, evidence_items[:2])
        sections.append(intro_section)

        # Create content sections based on evidence
        evidence_per_section = max(1, len(evidence_items) // max(1, len(spec.objectives)))

        for i, objective in enumerate(spec.objectives):
            start_idx = i * evidence_per_section
            end_idx = min(start_idx + evidence_per_section, len(evidence_items))
            section_evidence = evidence_items[start_idx:end_idx]

            section = self._create_content_section(spec, objective.description, section_evidence, i + 1)
            sections.append(section)

        # Create conclusion section
        conclusion_section = self._create_conclusion_section(spec, evidence_items[-2:])
        sections.append(conclusion_section)

        return sections

    def _create_introduction_section(
        self, spec: ChapterSpec, evidence: list[EvidenceItem]
    ) -> GeneratedSection:
        """Create introduction section with evidence."""
        paragraphs = []

        # Build introduction with evidence
        content = f"## Introduction\n\n"
        content += f"This chapter explores {spec.title}. "

        if evidence:
            first_evidence = evidence[0]
            content += f"Based on research, {first_evidence.claim}. "

        paragraphs.append(
            GeneratedParagraph(
                id=f"{spec.id}-intro-0",
                content=content,
                citations=[e.id for e in evidence],
                order=0,
            )
        )

        return GeneratedSection(
            id=f"{spec.id}-intro",
            title="Introduction",
            paragraphs=paragraphs,
            order=0,
        )

    def _create_content_section(
        self,
        spec: ChapterSpec,
        topic: str,
        evidence: list[EvidenceItem],
        section_num: int,
    ) -> GeneratedSection:
        """Create content section with evidence."""
        paragraphs = []

        section_title = f"Section {section_num}: {topic}"

        # Build content with evidence
        content = f"This section covers {topic}. "

        for e in evidence:
            content += f"{e.claim} "

        paragraphs.append(
            GeneratedParagraph(
                id=f"{spec.id}-s{section_num}-0",
                content=content,
                citations=[e.id for e in evidence],
                order=0,
            )
        )

        return GeneratedSection(
            id=f"{spec.id}-s{section_num}",
            title=section_title,
            paragraphs=paragraphs,
            order=section_num,
        )

    def _create_conclusion_section(
        self, spec: ChapterSpec, evidence: list[EvidenceItem]
    ) -> GeneratedSection:
        """Create conclusion section with evidence."""
        paragraphs = []

        content = f"In this chapter, we explored {spec.title}. "
        content += "The evidence presented supports the importance of these concepts."

        paragraphs.append(
            GeneratedParagraph(
                id=f"{spec.id}-conclusion-0",
                content=content,
                citations=[e.id for e in evidence],
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
        """Compile sections into full content."""
        lines = [f"# {title}", ""]

        for section in sections:
            lines.append(section.title)
            lines.append("")
            for paragraph in section.paragraphs:
                lines.append(paragraph.content)
                lines.append("")

        return "\n".join(lines)

    def _calculate_avg_confidence(self, evidence_items: list[EvidenceItem]) -> float:
        """Calculate average confidence across evidence items."""
        if not evidence_items:
            return 0.0

        total = sum(e.confidence for e in evidence_items)
        return total / len(evidence_items)