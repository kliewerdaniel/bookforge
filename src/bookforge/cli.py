"""Command-line interface for BookForge."""

import argparse
import sys
from pathlib import Path

from . import __version__


def main():
    """Main entry point for BookForge CLI."""
    parser = argparse.ArgumentParser(
        prog="bookforge",
        description="An Agentic Runtime for Synthesizing Technical Books from Knowledge Graphs",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new BookForge project")
    init_parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (default: current directory)",
    )

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a book from knowledge graph")
    generate_parser.add_argument(
        "graph_path",
        help="Path to the knowledge graph file",
    )
    generate_parser.add_argument(
        "--title",
        default="Untitled Book",
        help="Book title",
    )
    generate_parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory",
    )
    generate_parser.add_argument(
        "--formats",
        nargs="+",
        default=["html"],
        choices=["html", "pdf", "epub"],
        help="Output formats",
    )

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the BookForge API server")
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to",
    )

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()
        sys.exit(1)


def cmd_init(args):
    """Initialize a new BookForge project."""
    from .utils.storage import ArtifactStorage

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize storage
    storage = ArtifactStorage(str(output_dir / ".bookforge"))

    print(f"Initialized BookForge project in {output_dir}")
    print(f"Artifacts will be stored in {output_dir / '.bookforge'}")


def cmd_generate(args):
    """Generate a book from a knowledge graph."""
    from .knowledge.importer import GraphImporter
    from .knowledge.analyzer import GraphAnalyzer
    from .research.evidence import EvidenceCollector
    from .planning.themes import ThemeConstructor
    from .planning.blueprint import BlueprintGenerator
    from .writing.generator import ChapterGenerator
    from .publishing.compiler import BookCompiler
    from .utils.storage import ArtifactStorage

    # Initialize components
    importer = GraphImporter()
    analyzer = GraphAnalyzer()
    evidence_collector = EvidenceCollector()
    theme_constructor = ThemeConstructor()
    blueprint_generator = BlueprintGenerator()
    chapter_generator = ChapterGenerator()
    book_compiler = BookCompiler(args.output_dir)
    storage = ArtifactStorage()

    print(f"Generating book from {args.graph_path}...")

    # Step 1: Import knowledge graph
    print("1. Importing knowledge graph...")
    graph = importer.import_graph(args.graph_path)
    storage.save_artifact(graph.id, "graph", graph)
    print(f"   Imported {graph.node_count} nodes and {graph.edge_count} edges")

    # Step 2: Survey knowledge graph
    print("2. Surveying knowledge graph...")
    survey = analyzer.survey(graph)
    storage.save_artifact(f"survey-{graph.id}", "survey", survey)
    print(f"   Discovered {len(survey.concepts)} concepts")

    # Step 3: Construct themes
    print("3. Constructing themes...")
    theme_graph = theme_constructor.construct_themes(survey, graph)
    storage.save_artifact(theme_graph.id, "themes", theme_graph)
    print(f"   Created {len(theme_graph.themes)} themes")

    # Step 4: Generate blueprint
    print("4. Generating blueprint...")
    blueprint = blueprint_generator.generate(theme_graph, title=args.title)
    storage.save_artifact(blueprint.id, "blueprint", blueprint)
    print(f"   Created {len(blueprint.chapters)} chapters")

    # Step 5: Generate chapters
    print("5. Generating chapters...")
    chapters = []
    for i, chapter_spec in enumerate(blueprint.chapters):
        print(f"   Generating chapter {i + 1}/{len(blueprint.chapters)}...")
        chapter = chapter_generator.generate_chapter(chapter_spec)
        chapters.append(chapter)
        storage.save_artifact(chapter.id, "chapters", chapter)

    # Step 6: Compile book
    print("6. Compiling book...")
    compiled = book_compiler.compile(blueprint, chapters, args.formats)

    print(f"\nBook generated successfully!")
    print(f"Title: {args.title}")
    print(f"Chapters: {len(chapters)}")
    print(f"Total words: {sum(c.word_count for c in chapters)}")
    print(f"\nOutput files:")
    for fmt, path in compiled.formats.items():
        print(f"  {fmt}: {path}")


def cmd_serve(args):
    """Start the BookForge API server."""
    import uvicorn

    print(f"Starting BookForge API server on {args.host}:{args.port}...")
    uvicorn.run(
        "bookforge.api:app",
        host=args.host,
        port=args.port,
        reload=True,
    )


if __name__ == "__main__":
    main()