"""Script to analyze the DanielKliewer.com knowledge graph."""

import json
from pathlib import Path

from bookforge.knowledge.importer import GraphImporter
from bookforge.knowledge.analyzer import GraphAnalyzer
from bookforge.planning.themes import ThemeConstructor
from bookforge.planning.blueprint import BlueprintGenerator


def main():
    """Analyze the DanielKliewer.com knowledge graph."""
    print("=" * 70)
    print("DanielKliewer.com Knowledge Graph Analysis")
    print("=" * 70)

    # Import the knowledge graph
    print("\n1. Importing knowledge graph...")
    importer = GraphImporter()
    graph = importer.import_graph("data/graph/graph.json")

    print(f"   Graph: {graph.name}")
    print(f"   Description: {graph.description[:100]}...")
    print(f"   Nodes: {graph.node_count}")
    print(f"   Edges: {graph.edge_count}")

    # Analyze node types
    print("\n2. Node type distribution:")
    node_types = {}
    for node in graph.nodes:
        node_type = node.node_type
        node_types[node_type] = node_types.get(node_type, 0) + 1

    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
        print(f"   {node_type}: {count}")

    # Analyze the graph
    print("\n3. Analyzing knowledge graph...")
    analyzer = GraphAnalyzer()
    survey = analyzer.survey(graph)

    print(f"   Discovered {len(survey.concepts)} major concepts")
    print(f"   Identified {len(survey.relationships)} relationships")
    print(f"   Found {len(survey.gaps)} knowledge gaps")

    # Show top concepts
    print("\n4. Top 10 concepts by importance:")
    for i, concept in enumerate(survey.concepts[:10]):
        print(f"   {i + 1}. {concept.label} (centrality: {concept.centrality:.3f})")

    # Show knowledge gaps
    print("\n5. Knowledge gaps (top 5):")
    for i, gap in enumerate(survey.gaps[:5]):
        print(f"   {i + 1}. {gap.topic}: {gap.description}")

    # Construct themes
    print("\n6. Constructing themes...")
    theme_constructor = ThemeConstructor()
    theme_graph = theme_constructor.construct_themes(survey, graph, max_themes=10)

    print(f"   Created {len(theme_graph.themes)} themes")
    for i, theme in enumerate(theme_graph.themes):
        print(f"   {i + 1}. {theme.name} ({len(theme.concepts)} concepts)")

    # Generate blueprint
    print("\n7. Generating book blueprint...")
    blueprint_generator = BlueprintGenerator()
    blueprint = blueprint_generator.generate(
        theme_graph,
        title="Sovereign AI: A Technical Guide to Local-First Intelligent Systems",
        description="A comprehensive guide to building local-first intelligent systems from the DanielKliewer.com knowledge graph",
    )

    print(f"   Book: {blueprint.title}")
    print(f"   Parts: {len(blueprint.parts)}")
    print(f"   Chapters: {len(blueprint.chapters)}")
    print(f"   Target word count: {blueprint.total_word_count}")

    # Show chapter outline
    print("\n8. Chapter outline:")
    for i, chapter in enumerate(blueprint.chapters):
        print(f"   {i + 1}. {chapter.title} ({chapter.word_count_target} words)")

    # Save the blueprint
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)

    blueprint_data = {
        "id": blueprint.id,
        "title": blueprint.title,
        "description": blueprint.description,
        "parts": [
            {"id": p.id, "title": p.title, "description": p.description}
            for p in blueprint.parts
        ],
        "chapters": [
            {
                "id": c.id,
                "title": c.title,
                "theme_id": c.theme_id,
                "word_count_target": c.word_count_target,
                "objectives": [{"id": o.id, "description": o.description} for o in c.objectives],
            }
            for c in blueprint.chapters
        ],
    }

    with open(output_path / "blueprint.json", "w") as f:
        json.dump(blueprint_data, f, indent=2)

    print(f"\n   Blueprint saved to: {output_path / 'blueprint.json'}")

    # Save survey results
    survey_data = {
        "graph_id": survey.graph_id,
        "concepts": [
            {"id": c.id, "label": c.label, "centrality": c.centrality}
            for c in survey.concepts[:50]  # Top 50 concepts
        ],
        "gaps": [
            {"topic": g.topic, "description": g.description, "importance": g.importance}
            for g in survey.gaps
        ],
        "statistics": survey.statistics,
    }

    with open(output_path / "survey.json", "w") as f:
        json.dump(survey_data, f, indent=2)

    print(f"   Survey saved to: {output_path / 'survey.json'}")

    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()