"""Tests for book compiler."""

import pytest
from pathlib import Path
from bookforge.publishing.compiler import BookCompiler
from bookforge.planning.blueprint import BookBlueprint, ChapterSpec
from bookforge.writing.generator import GeneratedChapter


class TestBookCompiler:
    """Tests for BookCompiler."""

    def test_compile_html(self, tmp_path):
        """Test compiling to HTML."""
        compiler = BookCompiler(str(tmp_path))

        blueprint = BookBlueprint(
            id="bp-1",
            title="Test Book",
            chapters=[
                ChapterSpec(id="c1", title="Chapter 1", theme_id="t1"),
            ],
        )

        chapters = [
            GeneratedChapter(
                id="c1",
                title="Chapter 1",
                content="Test content",
                word_count=2,
            )
        ]

        compiled = compiler.compile(blueprint, chapters, ["html"])

        assert compiled.id.startswith("book-")
        assert compiled.title == "Test Book"
        assert "html" in compiled.formats
        assert compiled.total_word_count == 2

    def test_compile_multiple_formats(self, tmp_path):
        """Test compiling to multiple formats."""
        compiler = BookCompiler(str(tmp_path))

        blueprint = BookBlueprint(
            id="bp-1",
            title="Test Book",
            chapters=[],
        )

        compiled = compiler.compile(blueprint, [], ["html", "pdf"])

        assert "html" in compiled.formats
        assert "pdf" in compiled.formats

    def test_compiled_book_properties(self, tmp_path):
        """Test compiled book properties."""
        compiler = BookCompiler(str(tmp_path))

        blueprint = BookBlueprint(
            id="bp-1",
            title="Test Book",
            chapters=[],
        )

        chapters = [
            GeneratedChapter(id="c1", title="Ch 1", word_count=100),
            GeneratedChapter(id="c2", title="Ch 2", word_count=200),
        ]

        compiled = compiler.compile(blueprint, chapters, ["html"])

        assert compiled.chapter_count == 2
        assert compiled.total_word_count == 300