"""Script to generate a book blueprint from the DanielKliewer.com knowledge graph."""

import json
from pathlib import Path
from collections import Counter

from bookforge.knowledge.importer import GraphImporter
from bookforge.knowledge.analyzer import GraphAnalyzer
from bookforge.planning.themes import ThemeConstructor
from bookforge.planning.blueprint import BlueprintGenerator


def main():
    """Generate a book blueprint from the DanielKliewer.com knowledge graph."""
    print("=" * 70)
    print("BookForge: Generating Book Blueprint from Knowledge Graph")
    print("=" * 70)

    # Import the knowledge graph
    print("\n1. Importing knowledge graph...")
    importer = GraphImporter()
    graph = importer.import_graph("data/graph/graph.json")

    print(f"   Graph: {graph.name}")
    print(f"   Nodes: {graph.node_count}")
    print(f"   Edges: {graph.edge_count}")

    # Analyze the graph
    print("\n2. Analyzing knowledge graph...")
    analyzer = GraphAnalyzer()

    # Get articles and their tags for theme construction
    articles = [node for node in graph.nodes if node.node_type == "article"]
    all_tags = []
    for article in articles:
        tags = article.properties.get("tags", [])
        if isinstance(tags, list):
            all_tags.extend(tags)

    tag_counts = Counter(all_tags)
    print(f"   Found {len(articles)} articles with {len(tag_counts)} unique tags")

    # Show top themes based on tags
    print("\n3. Top themes from tags:")
    for tag, count in tag_counts.most_common(15):
        print(f"   - {tag}: {count} articles")

    # Create a simplified knowledge graph for theme construction
    print("\n4. Constructing themes...")

    # Group articles by major themes
    major_themes = {
        "Sovereign AI": ["sovereign AI", "sovereign ai", "privacy", "local AI", "local ai"],
        "Knowledge Graphs": ["Knowledge Graphs", "knowledge graphs", "graph databases", "Neo4j"],
        "Dynamic Persona MoE RAG": ["RAG", "rag", "Dynamic Persona", "MoE", "persona"],
        "Context Engineering": ["Context Engineering", "context engineering", "prompt engineering"],
        "Agentic Systems": ["AI Agents", "ai agents", "Agent", "agent", "MCP", "agentic"],
        "Local LLMs": ["Ollama", "ollama", "Local LLMs", "local llms", "llama"],
        "Web Development": ["Next.js", "next.js", "React", "react", "FastAPI", "fastapi"],
        "Machine Learning": ["Machine Learning", "machine learning", "ML", "ml", "deep learning"],
        "AI Development": ["AI Development", "ai development", "Python", "python", "Tutorial"],
        "Privacy & Security": ["Privacy", "privacy", "Security", "security", "encryption"],
    }

    # Create themes based on article tags
    themes = []
    for theme_name, theme_tags in major_themes.items():
        theme_articles = []
        for article in articles:
            article_tags = article.properties.get("tags", [])
            if isinstance(article_tags, list):
                if any(tag in theme_tags for tag in article_tags):
                    theme_articles.append(article)

        if theme_articles:
            themes.append({
                "name": theme_name,
                "article_count": len(theme_articles),
                "articles": [a.label for a in theme_articles[:5]],
            })

    # Sort by article count
    themes.sort(key=lambda x: x["article_count"], reverse=True)

    print("   Constructed themes:")
    for i, theme in enumerate(themes):
        print(f"   {i + 1}. {theme['name']} ({theme['article_count']} articles)")

    # Generate book blueprint
    print("\n5. Generating book blueprint...")

    # Create a book structure based on the themes
    book_title = "Sovereign AI: Building Local-First Intelligent Systems"
    book_description = "A comprehensive guide to building sovereign AI systems using local-first architectures, knowledge graphs, and agentic systems, synthesized from the DanielKliewer.com knowledge graph."

    # Create parts and chapters
    parts = []
    chapters = []
    chapter_id = 0

    for i, theme in enumerate(themes[:10]):  # Top 10 themes
        part_id = f"part-{i}"
        part = {
            "id": part_id,
            "title": theme["name"],
            "description": f"Part covering {theme['name']} concepts and implementations",
            "chapters": [],
        }

        # Create 2-3 chapters per theme
        num_chapters = min(3, max(1, theme["article_count"] // 5))
        for j in range(num_chapters):
            chapter = {
                "id": f"chapter-{chapter_id}",
                "title": f"{theme['name']} - Chapter {j + 1}",
                "theme_id": part_id,
                "word_count_target": 5000,
                "articles": theme["articles"][:3],
            }
            chapters.append(chapter)
            part["chapters"].append(chapter["id"])
            chapter_id += 1

        parts.append(part)

    # Create the blueprint
    blueprint = {
        "id": "blueprint-sovereign-ai",
        "title": book_title,
        "description": book_description,
        "parts": parts,
        "chapters": chapters,
        "learning_objectives": [
            "Understand sovereign AI principles and local-first architectures",
            "Design and implement knowledge graphs for technical documentation",
            "Build agentic systems using local LLMs and MCP",
            "Implement Dynamic Persona MoE RAG systems",
            "Apply context engineering techniques for AI systems",
            "Deploy privacy-preserving AI solutions",
        ],
        "metadata": {
            "source": "danielkliewer.com",
            "article_count": len(articles),
            "theme_count": len(themes),
            "total_target_words": len(chapters) * 5000,
        },
    }

    # Save the blueprint
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)

    with open(output_path / "book_blueprint.json", "w") as f:
        json.dump(blueprint, f, indent=2)

    print(f"\n   Book: {book_title}")
    print(f"   Description: {book_description}")
    print(f"   Parts: {len(parts)}")
    print(f"   Chapters: {len(chapters)}")
    print(f"   Target word count: {len(chapters) * 5000}")
    print(f"\n   Blueprint saved to: {output_path / 'book_blueprint.json'}")

    # Save theme details
    theme_details = {
        "themes": themes,
        "learning_objectives": blueprint["learning_objectives"],
    }

    with open(output_path / "theme_details.json", "w") as f:
        json.dump(theme_details, f, indent=2)

    print(f"   Theme details saved to: {output_path / 'theme_details.json'}")

    print("\n" + "=" * 70)
    print("Blueprint Generation Complete!")
    print("=" * 70)

    # Show chapter outline
    print("\nChapter Outline:")
    for i, chapter in enumerate(chapters):
        print(f"   {i + 1}. {chapter['title']} ({chapter['word_count_target']} words)")


if __name__ == "__main__":
    main()