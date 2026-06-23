"""Tests for chapter generator."""

import pytest
from bookforge.writing.generator import ChapterGenerator, GeneratedChapter
from bookforge.planning.blueprint import ChapterSpec, LearningObjective


class TestChapterGenerator:
    """Tests for ChapterGenerator."""

    def test_generate_chapter(self):
        """Test generating a chapter from specification."""
        spec = ChapterSpec(
            id="chapter-1",
            title="Introduction to Concepts",
            theme_id="theme-1",
            objectives=[
                LearningObjective(
                    id="obj-1",
                    description="Understand basic concepts",
                    level="understand",
                )
            ],
            word_count_target=1000,
        )

        generator = ChapterGenerator()
        chapter = generator.generate_chapter(spec)

        assert chapter.id == "chapter-1"
        assert chapter.title == "Introduction to Concepts"
        assert chapter.word_count > 0
        assert len(chapter.sections) > 0

    def test_calculate_word_count(self):
        """Test word count calculation."""
        chapter = GeneratedChapter(
            id="chapter-1",
            title="Test Chapter",
            content="This is a test chapter with some words.",
        )
        word_count = chapter.calculate_word_count()
        assert word_count == 8

    def test_generate_with_multiple_objectives(self):
        """Test generating chapter with multiple objectives."""
        spec = ChapterSpec(
            id="chapter-2",
            title="Advanced Topics",
            theme_id="theme-1",
            objectives=[
                LearningObjective(id="obj-1", description="Learn topic A"),
                LearningObjective(id="obj-2", description="Learn topic B"),
                LearningObjective(id="obj-3", description="Learn topic C"),
            ],
        )

        generator = ChapterGenerator()
        chapter = generator.generate_chapter(spec)

        # Should have introduction + 3 sections + conclusion
        assert len(chapter.sections) == 5