"""Tests for review agents."""

import pytest
from bookforge.agents.reviewer import TechnicalReviewer, EditorialReviewer, CitationReviewer
from bookforge.writing.generator import GeneratedChapter, GeneratedSection, GeneratedParagraph


class TestTechnicalReviewer:
    """Tests for TechnicalReviewer."""

    def test_review_chapter(self):
        """Test reviewing a chapter."""
        chapter = GeneratedChapter(
            id="chapter-1",
            title="Test Chapter",
            content="This is a test chapter.",
            sections=[
                GeneratedSection(
                    id="s1",
                    title="Section 1",
                    paragraphs=[
                        GeneratedParagraph(
                            id="p1",
                            content="Test paragraph.",
                            citations=["ref-1"],
                        )
                    ],
                )
            ],
        )

        reviewer = TechnicalReviewer()
        result = reviewer.process(chapter)

        assert result.success
        assert result.output is not None
        assert result.output.chapter_id == "chapter-1"

    def test_review_empty_chapter(self):
        """Test reviewing an empty chapter."""
        chapter = GeneratedChapter(
            id="empty",
            title="Empty",
            content="",
        )

        reviewer = TechnicalReviewer()
        result = reviewer.process(chapter)

        assert result.success


class TestEditorialReviewer:
    """Tests for EditorialReviewer."""

    def test_review_chapter(self):
        """Test reviewing a chapter."""
        chapter = GeneratedChapter(
            id="chapter-1",
            title="Test Chapter",
            content="This is a test chapter with some content.",
        )

        reviewer = EditorialReviewer()
        result = reviewer.process(chapter)

        assert result.success
        assert result.output is not None


class TestCitationReviewer:
    """Tests for CitationReviewer."""

    def test_review_chapter_with_citations(self):
        """Test reviewing a chapter with citations."""
        chapter = GeneratedChapter(
            id="chapter-1",
            title="Test Chapter",
            content="This is a test chapter.",
            citations=["ref-1", "ref-2"],
        )

        reviewer = CitationReviewer()
        result = reviewer.process(chapter)

        assert result.success
        assert result.output is not None

    def test_review_chapter_without_citations(self):
        """Test reviewing a chapter without citations."""
        chapter = GeneratedChapter(
            id="chapter-1",
            title="Test Chapter",
            content="This is a test chapter with content that should have citations.",
        )

        reviewer = CitationReviewer()
        result = reviewer.process(chapter)

        assert result.success
        # Should have issues about missing citations
        assert len(result.output.issues) > 0