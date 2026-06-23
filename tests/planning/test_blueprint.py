"""Tests for blueprint generator."""

import pytest
from bookforge.planning.blueprint import BlueprintGenerator, BookBlueprint
from bookforge.planning.themes import ThemeGraph, Theme


class TestBlueprintGenerator:
    """Tests for BlueprintGenerator."""

    def test_generate_blueprint(self):
        """Test generating a blueprint from themes."""
        theme_graph = ThemeGraph(
            id="tg-1",
            themes=[
                Theme(
                    id="t1",
                    name="Theme 1",
                    description="First theme",
                    concepts=["c1", "c2"],
                ),
                Theme(
                    id="t2",
                    name="Theme 2",
                    description="Second theme",
                    concepts=["c3", "c4"],
                ),
            ],
        )

        generator = BlueprintGenerator()
        blueprint = generator.generate(theme_graph, title="Test Book")

        assert blueprint.id == "blueprint-tg-1"
        assert blueprint.title == "Test Book"
        assert len(blueprint.parts) == 2
        assert len(blueprint.chapters) == 2

    def test_blueprint_word_count(self):
        """Test blueprint word count calculation."""
        from bookforge.planning.blueprint import ChapterSpec

        blueprint = BookBlueprint(
            id="bp-1",
            title="Test",
            chapters=[
                ChapterSpec(id="c1", title="Ch 1", theme_id="t1", word_count_target=5000),
                ChapterSpec(id="c2", title="Ch 2", theme_id="t2", word_count_target=3000),
            ],
        )

        assert blueprint.total_word_count == 8000

    def test_get_chapter(self):
        """Test getting a chapter by ID."""
        from bookforge.planning.blueprint import ChapterSpec

        blueprint = BookBlueprint(
            id="bp-1",
            title="Test",
            chapters=[
                ChapterSpec(id="c1", title="Ch 1", theme_id="t1"),
            ],
        )

        chapter = blueprint.get_chapter("c1")
        assert chapter is not None
        assert chapter.id == "c1"

        chapter = blueprint.get_chapter("nonexistent")
        assert chapter is None