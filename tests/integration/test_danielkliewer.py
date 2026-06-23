"""Integration test for BookForge with real DanielKliewer.com data."""

import json
import pytest
from pathlib import Path

from bookforge.knowledge.importer import GraphImporter
from bookforge.knowledge.analyzer import GraphAnalyzer
from bookforge.research.evidence import EvidenceCollector, EvidenceSource
from bookforge.planning.themes import ThemeConstructor
from bookforge.planning.blueprint import BlueprintGenerator, ChapterSpec, LearningObjective
from bookforge.writing.generator import ChapterGenerator
from bookforge.writing.evidence_writing import EvidenceBackedWriter
from bookforge.publishing.compiler import BookCompiler
from bookforge.agents.reviewer import TechnicalReviewer, EditorialReviewer


class TestDanielKliewerIntegration:
    """Integration tests with real DanielKliewer.com data."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.graph_path = Path("data/graph/graph.json")
        self.importer = GraphImporter()
        self.analyzer = GraphAnalyzer()
        self.evidence_collector = EvidenceCollector()
        self.theme_constructor = ThemeConstructor()
        self.blueprint_generator = BlueprintGenerator()
        self.chapter_generator = ChapterGenerator()
        self.evidence_writer = EvidenceBackedWriter(self.evidence_collector)
        self.book_compiler = BookCompiler("output/test")
        self.technical_reviewer = TechnicalReviewer()
        self.editorial_reviewer = EditorialReviewer()

    def test_import_danielkliewer_graph(self):
        """Test importing the DanielKliewer.com knowledge graph."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        graph = self.importer.import_graph(str(self.graph_path))

        assert graph.id == "danielkliewer"
        assert graph.name == "DanielKliewer.com Knowledge Graph"
        assert graph.node_count > 0
        assert graph.edge_count > 0

        # Check node types
        node_types = set(node.node_type for node in graph.nodes)
        assert "article" in node_types
        assert "concept" in node_types
        assert "tool" in node_types
        assert "project" in node_types

    def test_analyze_danielkliewer_graph(self):
        """Test analyzing the DanielKliewer.com knowledge graph."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        graph = self.importer.import_graph(str(self.graph_path))
        survey = self.analyzer.survey(graph)

        assert len(survey.concepts) > 0
        assert len(survey.gaps) > 0
        assert survey.statistics["node_count"] > 0

    def test_construct_themes_from_danielkliewer(self):
        """Test constructing themes from DanielKliewer.com graph."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        graph = self.importer.import_graph(str(self.graph_path))
        survey = self.analyzer.survey(graph)
        theme_graph = self.theme_constructor.construct_themes(survey, graph, max_themes=5)

        assert len(theme_graph.themes) > 0
        assert len(theme_graph.themes) <= 5

    def test_generate_blueprint_from_danielkliewer(self):
        """Test generating blueprint from DanielKliewer.com graph."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        graph = self.importer.import_graph(str(self.graph_path))
        survey = self.analyzer.survey(graph)
        theme_graph = self.theme_constructor.construct_themes(survey, graph, max_themes=5)
        blueprint = self.blueprint_generator.generate(
            theme_graph,
            title="Sovereign AI: A Technical Guide",
        )

        assert blueprint.title == "Sovereign AI: A Technical Guide"
        assert len(blueprint.parts) > 0
        assert len(blueprint.chapters) > 0
        assert blueprint.total_word_count > 0

    def test_collect_evidence_from_articles(self):
        """Test collecting evidence from DanielKliewer.com articles."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        graph = self.importer.import_graph(str(self.graph_path))
        articles = [node for node in graph.nodes if node.node_type == "article"]

        # Add articles as evidence sources
        for article in articles[:10]:  # Use first 10 articles
            evidence_source = EvidenceSource(
                id=article.id,
                title=article.label,
                source_type="blog_post",
                content=article.properties.get("text", "")[:500],
                reliability=0.8,
            )
            self.evidence_collector.add_source(evidence_source)

        assert len(self.evidence_collector.sources) == 10

        # Collect evidence for a claim
        evidence = self.evidence_collector.collect_evidence(
            "Sovereign AI requires local-first architecture"
        )

        assert evidence.claim == "Sovereign AI requires local-first architecture"
        assert len(evidence.sources) >= 0

    def test_generate_chapter_with_evidence(self):
        """Test generating a chapter with evidence from DanielKliewer.com."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        graph = self.importer.import_graph(str(self.graph_path))
        articles = [node for node in graph.nodes if node.node_type == "article"]

        # Add articles as evidence sources
        for article in articles[:5]:
            evidence_source = EvidenceSource(
                id=article.id,
                title=article.label,
                source_type="blog_post",
                content=article.properties.get("text", "")[:500],
                reliability=0.8,
            )
            self.evidence_collector.add_source(evidence_source)

        # Create chapter specification
        spec = ChapterSpec(
            id="test-chapter",
            title="Introduction to Sovereign AI",
            theme_id="theme-1",
            objectives=[
                LearningObjective(
                    id="obj-1",
                    description="Understand sovereign AI principles",
                    level="understand",
                )
            ],
            word_count_target=2000,
        )

        # Generate chapter
        chapter = self.evidence_writer.write_with_evidence(spec)

        assert chapter.id == "test-chapter"
        assert chapter.title == "Introduction to Sovereign AI"
        assert chapter.word_count > 0

    def test_review_generated_chapter(self):
        """Test reviewing a generated chapter."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        # Generate a simple chapter
        spec = ChapterSpec(
            id="review-test",
            title="Test Chapter",
            theme_id="theme-1",
            objectives=[
                LearningObjective(
                    id="obj-1",
                    description="Test objective",
                    level="understand",
                )
            ],
        )

        chapter = self.chapter_generator.generate_chapter(spec)

        # Review the chapter
        tech_result = self.technical_reviewer.process(chapter)
        editorial_result = self.editorial_reviewer.process(chapter)

        assert tech_result.success
        assert editorial_result.success
        assert tech_result.output.score >= 0
        assert editorial_result.output.score >= 0

    def test_compile_book_with_real_data(self):
        """Test compiling a book with real DanielKliewer.com data."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        graph = self.importer.import_graph(str(self.graph_path))
        survey = self.analyzer.survey(graph)
        theme_graph = self.theme_constructor.construct_themes(survey, graph, max_themes=3)
        blueprint = self.blueprint_generator.generate(
            theme_graph,
            title="Test Book",
        )

        # Generate chapters
        chapters = []
        for spec in blueprint.chapters[:2]:  # Generate 2 chapters
            chapter = self.chapter_generator.generate_chapter(spec)
            chapters.append(chapter)

        # Compile book
        compiled = self.book_compiler.compile(blueprint, chapters, ["html"])

        assert compiled.title == "Test Book"
        assert len(compiled.formats) > 0
        assert "html" in compiled.formats

    def test_full_pipeline_danielkliewer(self):
        """Test the full BookForge pipeline with DanielKliewer.com data."""
        if not self.graph_path.exists():
            pytest.skip("DanielKliewer.com graph not available")

        # Step 1: Import graph
        graph = self.importer.import_graph(str(self.graph_path))
        assert graph.node_count > 0

        # Step 2: Analyze graph
        survey = self.analyzer.survey(graph)
        assert len(survey.concepts) > 0

        # Step 3: Construct themes
        theme_graph = self.theme_constructor.construct_themes(survey, graph, max_themes=3)
        assert len(theme_graph.themes) > 0

        # Step 4: Generate blueprint
        blueprint = self.blueprint_generator.generate(
            theme_graph,
            title="Sovereign AI Guide",
        )
        assert len(blueprint.chapters) > 0

        # Step 5: Generate chapters
        chapters = []
        for spec in blueprint.chapters[:2]:
            chapter = self.chapter_generator.generate_chapter(spec)
            chapters.append(chapter)
        assert len(chapters) > 0

        # Step 6: Review chapters
        for chapter in chapters:
            result = self.technical_reviewer.process(chapter)
            assert result.success

        # Step 7: Compile book
        compiled = self.book_compiler.compile(blueprint, chapters, ["html"])
        assert len(compiled.formats) > 0

        print(f"\nFull pipeline test passed!")
        print(f"Graph: {graph.node_count} nodes")
        print(f"Themes: {len(theme_graph.themes)}")
        print(f"Chapters: {len(chapters)}")
        print(f"Output: {compiled.formats}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])