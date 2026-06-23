"""Example script demonstrating BookForge usage."""

import json
from pathlib import Path

from bookforge.knowledge.importer import GraphImporter
from bookforge.knowledge.analyzer import GraphAnalyzer
from bookforge.research.evidence import EvidenceCollector, EvidenceSource
from bookforge.planning.themes import ThemeConstructor
from bookforge.planning.blueprint import BlueprintGenerator
from bookforge.writing.generator import ChapterGenerator
from bookforge.publishing.compiler import BookCompiler
from bookforge.agents.reviewer import TechnicalReviewer, EditorialReviewer


def create_sample_knowledge_graph():
    """Create a sample knowledge graph for demonstration."""
    graph_data = {
        "id": "sovereign-ai-graph",
        "name": "Sovereign AI Knowledge Graph",
        "nodes": [
            {"id": "sovereign-ai", "label": "Sovereign AI", "type": "concept"},
            {"id": "knowledge-graphs", "label": "Knowledge Graphs", "type": "concept"},
            {"id": "context-engineering", "label": "Context Engineering", "type": "concept"},
            {"id": "agentic-systems", "label": "Agentic Systems", "type": "concept"},
            {"id": "local-inference", "label": "Local Inference", "type": "concept"},
            {"id": "privacy", "label": "Privacy", "type": "concept"},
            {"id": "deterministic", "label": "Deterministic Behavior", "type": "concept"},
            {"id": "moe-rag", "label": "MoE RAG", "type": "concept"},
        ],
        "edges": [
            {"source": "sovereign-ai", "target": "knowledge-graphs", "type": "uses"},
            {"source": "sovereign-ai", "target": "local-inference", "type": "requires"},
            {"source": "sovereign-ai", "target": "privacy", "type": "ensures"},
            {"source": "knowledge-graphs", "target": "context-engineering", "type": "enables"},
            {"source": "agentic-systems", "target": "knowledge-graphs", "type": "utilizes"},
            {"source": "agentic-systems", "target": "context-engineering", "type": "requires"},
            {"source": "moe-rag", "target": "knowledge-graphs", "type": "uses"},
            {"source": "moe-rag", "target": "context-engineering", "type": "implements"},
            {"source": "context-engineering", "target": "deterministic", "type": "promotes"},
        ],
    }

    # Write sample graph
    graph_path = Path("sample_graph.json")
    with open(graph_path, "w") as f:
        json.dump(graph_data, f, indent=2)

    return graph_path


def main():
    """Demonstrate BookForge pipeline."""
    print("=" * 60)
    print("BookForge Demo - Agentic Technical Book Synthesis")
    print("=" * 60)

    # Create sample knowledge graph
    print("\n1. Creating sample knowledge graph...")
    graph_path = create_sample_knowledge_graph()
    print(f"   Created: {graph_path}")

    # Import knowledge graph
    print("\n2. Importing knowledge graph...")
    importer = GraphImporter()
    graph = importer.import_graph(str(graph_path))
    print(f"   Imported {graph.node_count} nodes and {graph.edge_count} edges")

    # Survey knowledge graph
    print("\n3. Surveying knowledge graph...")
    analyzer = GraphAnalyzer()
    survey = analyzer.survey(graph)
    print(f"   Discovered {len(survey.concepts)} concepts")
    print(f"   Identified {len(survey.gaps)} knowledge gaps")

    # Construct themes
    print("\n4. Constructing themes...")
    theme_constructor = ThemeConstructor()
    theme_graph = theme_constructor.construct_themes(survey, graph)
    print(f"   Created {len(theme_graph.themes)} themes")

    # Generate blueprint
    print("\n5. Generating book blueprint...")
    blueprint_generator = BlueprintGenerator()
    blueprint = blueprint_generator.generate(
        theme_graph,
        title="Sovereign AI: A Technical Guide",
        description="A comprehensive guide to building local-first intelligent systems",
    )
    print(f"   Created {len(blueprint.chapters)} chapters")
    print(f"   Total target words: {blueprint.total_word_count}")

    # Generate chapters
    print("\n6. Generating chapters...")
    chapter_generator = ChapterGenerator()
    chapters = []
    for i, chapter_spec in enumerate(blueprint.chapters):
        print(f"   Generating chapter {i + 1}/{len(blueprint.chapters)}...")
        chapter = chapter_generator.generate_chapter(chapter_spec)
        chapters.append(chapter)

    # Review chapters
    print("\n7. Reviewing chapters...")
    technical_reviewer = TechnicalReviewer()
    editorial_reviewer = EditorialReviewer()

    for chapter in chapters[:2]:  # Review first 2 chapters
        tech_result = technical_reviewer.process(chapter)
        print(f"   {chapter.title}: Technical score = {tech_result.output.score:.2f}")

    # Compile book
    print("\n8. Compiling book...")
    compiler = BookCompiler("output")
    compiled = compiler.compile(blueprint, chapters, ["html"])

    print(f"\n{'=' * 60}")
    print("BookForge Demo Complete!")
    print(f"{'=' * 60}")
    print(f"\nOutput files:")
    for fmt, path in compiled.formats.items():
        print(f"  {fmt}: {path}")

    # Clean up
    graph_path.unlink()

    print(f"\nTo start the API server, run:")
    print(f"  bookforge serve")


if __name__ == "__main__":
    main()