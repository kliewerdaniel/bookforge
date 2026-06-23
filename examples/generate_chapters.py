"""Script to generate sample chapters from the DanielKliewer.com knowledge graph."""

import json
from pathlib import Path
from collections import Counter

from bookforge.knowledge.importer import GraphImporter
from bookforge.writing.generator import ChapterGenerator
from bookforge.writing.evidence_writing import EvidenceBackedWriter
from bookforge.research.evidence import EvidenceCollector, EvidenceSource
from bookforge.publishing.compiler import BookCompiler


def main():
    """Generate sample chapters from the DanielKliewer.com knowledge graph."""
    print("=" * 70)
    print("BookForge: Generating Sample Chapters")
    print("=" * 70)

    # Import the knowledge graph
    print("\n1. Importing knowledge graph...")
    importer = GraphImporter()
    graph = importer.import_graph("data/graph/graph.json")

    # Load the blueprint
    print("\n2. Loading blueprint...")
    with open("output/book_blueprint.json", "r") as f:
        blueprint_data = json.load(f)

    print(f"   Book: {blueprint_data['title']}")
    print(f"   Parts: {len(blueprint_data['parts'])}")
    print(f"   Chapters: {len(blueprint_data['chapters'])}")

    # Get articles for evidence
    print("\n3. Collecting evidence from articles...")
    articles = [node for node in graph.nodes if node.node_type == "article"]
    print(f"   Found {len(articles)} articles")

    # Create evidence collector
    evidence_collector = EvidenceCollector()

    # Add articles as evidence sources
    for article in articles[:50]:  # Use first 50 articles
        evidence_source = EvidenceSource(
            id=article.id,
            title=article.label,
            source_type="blog_post",
            content=article.properties.get("text", "")[:1000],  # First 1000 chars
            reliability=0.8,
            metadata={
                "date": article.properties.get("date"),
                "tags": article.properties.get("tags", []),
            },
        )
        evidence_collector.add_source(evidence_source)

    print(f"   Added {len(evidence_collector.sources)} evidence sources")

    # Generate chapters
    print("\n4. Generating sample chapters...")
    chapter_generator = ChapterGenerator()
    evidence_writer = EvidenceBackedWriter(evidence_collector)

    # Generate first 3 chapters as samples
    sample_chapters = blueprint_data["chapters"][:3]
    generated_chapters = []

    for i, chapter_data in enumerate(sample_chapters):
        print(f"\n   Generating chapter {i + 1}: {chapter_data['title']}...")

        # Create chapter specification
        from bookforge.planning.blueprint import ChapterSpec, LearningObjective

        spec = ChapterSpec(
            id=chapter_data["id"],
            title=chapter_data["title"],
            theme_id=chapter_data["theme_id"],
            objectives=[
                LearningObjective(
                    id=f"obj-{i}",
                    description=f"Understand {chapter_data['title']}",
                    level="understand",
                )
            ],
            word_count_target=chapter_data["word_count_target"],
        )

        # Generate chapter with evidence
        chapter = evidence_writer.write_with_evidence(spec)
        generated_chapters.append(chapter)

        print(f"      Generated {chapter.word_count} words")
        print(f"      Sections: {len(chapter.sections)}")
        print(f"      Citations: {len(chapter.citations)}")

    # Compile book
    print("\n5. Compiling book...")
    compiler = BookCompiler("output")

    # Create a simple blueprint for compilation
    from bookforge.planning.blueprint import BookBlueprint, BookPart

    compilation_blueprint = BookBlueprint(
        id=blueprint_data["id"],
        title=blueprint_data["title"],
        description=blueprint_data["description"],
        parts=[
            BookPart(
                id=p["id"],
                title=p["title"],
                description=p["description"],
                chapters=p["chapters"],
            )
            for p in blueprint_data["parts"]
        ],
        chapters=[],  # Will be populated from generated chapters
    )

    # Compile to HTML
    compiled = compiler.compile(compilation_blueprint, generated_chapters, ["html"])

    print(f"\n   Compiled book: {compiled.title}")
    print(f"   Output files:")
    for fmt, path in compiled.formats.items():
        print(f"   - {fmt}: {path}")

    # Save generated chapters
    print("\n6. Saving generated chapters...")
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)

    for i, chapter in enumerate(generated_chapters):
        chapter_data = {
            "id": chapter.id,
            "title": chapter.title,
            "content": chapter.content,
            "word_count": chapter.word_count,
            "sections": [
                {
                    "id": s.id,
                    "title": s.title,
                    "paragraphs": [
                        {"id": p.id, "content": p.content}
                        for p in s.paragraphs
                    ],
                }
                for s in chapter.sections
            ],
            "citations": chapter.citations,
        }

        chapter_file = output_path / f"chapter_{i + 1}.json"
        with open(chapter_file, "w") as f:
            json.dump(chapter_data, f, indent=2)

        print(f"   Saved: {chapter_file}")

    # Save compilation result
    compilation_data = {
        "id": compiled.id,
        "title": compiled.title,
        "formats": compiled.formats,
        "metadata": compiled.metadata,
    }

    with open(output_path / "compilation.json", "w") as f:
        json.dump(compilation_data, f, indent=2)

    print(f"\n   Compilation data saved to: {output_path / 'compilation.json'}")

    print("\n" + "=" * 70)
    print("Chapter Generation Complete!")
    print("=" * 70)

    # Show sample content
    print("\nSample Chapter Content (Chapter 1, first 500 chars):")
    if generated_chapters:
        print("-" * 50)
        print(generated_chapters[0].content[:500])
        print("-" * 50)


if __name__ == "__main__":
    main()