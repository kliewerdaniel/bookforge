"""Script to analyze the DanielKliewer.com knowledge graph."""

import json
from pathlib import Path
from collections import Counter

from bookforge.knowledge.importer import GraphImporter


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
    node_types = Counter(node.node_type for node in graph.nodes)
    for node_type, count in node_types.most_common():
        print(f"   {node_type}: {count}")

    # Analyze articles
    print("\n3. Articles analysis:")
    articles = [node for node in graph.nodes if node.node_type == "article"]
    print(f"   Total articles: {len(articles)}")

    # Get date distribution
    dates = []
    for article in articles:
        date = article.properties.get("date", "")
        if date:
            # Extract year-month
            if isinstance(date, str) and len(date) >= 7:
                dates.append(date[:7])

    date_counts = Counter(dates)
    print("\n   Articles by year-month (top 10):")
    for date, count in date_counts.most_common(10):
        print(f"   {date}: {count}")

    # Analyze tags
    print("\n4. Tag analysis:")
    all_tags = []
    for article in articles:
        tags = article.properties.get("tags", [])
        if isinstance(tags, list):
            all_tags.extend(tags)

    tag_counts = Counter(all_tags)
    print("   Top 20 tags:")
    for tag, count in tag_counts.most_common(20):
        print(f"   {tag}: {count}")

    # Analyze concepts
    print("\n5. Concept analysis:")
    concepts = [node for node in graph.nodes if node.node_type == "concept"]
    print(f"   Total concepts: {len(concepts)}")

    # Show some sample concepts
    print("\n   Sample concepts:")
    for concept in concepts[:20]:
        print(f"   - {concept.label}")

    # Analyze tools
    print("\n6. Tool analysis:")
    tools = [node for node in graph.nodes if node.node_type == "tool"]
    print(f"   Total tools: {len(tools)}")

    # Show some sample tools
    print("\n   Sample tools:")
    for tool in tools[:20]:
        print(f"   - {tool.label}")

    # Analyze projects
    print("\n7. Project analysis:")
    projects = [node for node in graph.nodes if node.node_type == "project"]
    print(f"   Total projects: {len(projects)}")

    # Show some sample projects
    print("\n   Sample projects:")
    for project in projects[:20]:
        print(f"   - {project.label}")

    # Save summary
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)

    summary = {
        "graph_name": graph.name,
        "description": graph.description,
        "total_nodes": graph.node_count,
        "total_edges": graph.edge_count,
        "node_types": dict(node_types),
        "article_count": len(articles),
        "concept_count": len(concepts),
        "tool_count": len(tools),
        "project_count": len(projects),
        "top_tags": dict(tag_counts.most_common(50)),
    }

    with open(output_path / "graph_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n   Summary saved to: {output_path / 'graph_summary.json'}")

    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()