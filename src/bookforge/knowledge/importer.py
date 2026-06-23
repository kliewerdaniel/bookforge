"""Graph importer for loading knowledge graphs from various sources."""

import json
from pathlib import Path
from typing import Any

import yaml

from .graph import GraphEdge, GraphNode, KnowledgeGraph


class GraphImporter:
    """Imports knowledge graphs from various formats."""

    def import_graph(self, graph_path: str, format: str = "auto") -> KnowledgeGraph:
        """Import a knowledge graph from a file.

        Args:
            graph_path: Path to the graph file
            format: Graph format (auto, sovereignspec, json, yaml, markdown)

        Returns:
            Imported knowledge graph
        """
        path = Path(graph_path)
        if not path.exists():
            raise FileNotFoundError(f"Graph file not found: {graph_path}")

        if format == "auto":
            format = self._detect_format(path)

        if format == "json":
            return self._import_json(path)
        elif format == "danielkliewer":
            return self._import_danielkliewer(path)
        elif format == "yaml":
            return self._import_yaml(path)
        elif format == "sovereignspec":
            return self._import_sovereignspec(path)
        elif format == "markdown":
            return self._import_markdown(path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _detect_format(self, path: Path) -> str:
        """Detect the format of a graph file."""
        suffix = path.suffix.lower()
        if suffix == ".json":
            # Check if it's the DanielKliewer.com format
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "nodes" in data and len(data.get("nodes", [])) > 0:
                    first_node = data["nodes"][0]
                    if "type" in first_node and "provenance" in first_node:
                        return "danielkliewer"
            return "json"
        elif suffix in (".yaml", ".yml"):
            return "yaml"
        elif suffix == ".md":
            return "markdown"
        elif suffix == ".sspec":
            return "sovereignspec"
        else:
            # Try to detect from content
            with open(path, "r", encoding="utf-8") as f:
                content = f.read(1000)
                if content.strip().startswith("{"):
                    return "json"
                elif "id:" in content and "nodes:" in content:
                    return "yaml"
                return "markdown"

    def _import_json(self, path: Path) -> KnowledgeGraph:
        """Import a graph from JSON format."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        nodes = [
            GraphNode(
                id=node["id"],
                label=node.get("label", node["id"]),
                node_type=node.get("type", "concept"),
                properties=node.get("properties", {}),
            )
            for node in data.get("nodes", [])
        ]

        edges = [
            GraphEdge(
                id=edge.get("id", f"{edge['source']}-{edge['target']}"),
                source=edge["source"],
                target=edge["target"],
                edge_type=edge.get("type", "related_to"),
                weight=edge.get("weight", 1.0),
                properties=edge.get("properties", {}),
            )
            for edge in data.get("edges", [])
        ]

        return KnowledgeGraph(
            id=data.get("id", path.stem),
            name=data.get("name", path.stem),
            description=data.get("description", ""),
            nodes=nodes,
            edges=edges,
            metadata=data.get("metadata", {}),
        )

    def _import_yaml(self, path: Path) -> KnowledgeGraph:
        """Import a graph from YAML format."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        nodes = [
            GraphNode(
                id=node["id"],
                label=node.get("label", node["id"]),
                node_type=node.get("type", "concept"),
                properties=node.get("properties", {}),
            )
            for node in data.get("nodes", [])
        ]

        edges = [
            GraphEdge(
                id=edge.get("id", f"{edge['source']}-{edge['target']}"),
                source=edge["source"],
                target=edge["target"],
                edge_type=edge.get("type", "related_to"),
                weight=edge.get("weight", 1.0),
                properties=edge.get("properties", {}),
            )
            for edge in data.get("edges", [])
        ]

        return KnowledgeGraph(
            id=data.get("id", path.stem),
            name=data.get("name", path.stem),
            description=data.get("description", ""),
            nodes=nodes,
            edges=edges,
            metadata=data.get("metadata", {}),
        )

    def _import_sovereignspec(self, path: Path) -> KnowledgeGraph:
        """Import a graph from SovereignSpec format."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        nodes = []
        edges = []

        # Create a node for the spec itself
        spec_id = data.get("id", path.stem)
        nodes.append(
            GraphNode(
                id=f"spec-{spec_id}",
                label=data.get("title", spec_id),
                node_type="specification",
                properties={
                    "version": data.get("version"),
                    "status": data.get("status"),
                    "purpose": data.get("purpose"),
                },
            )
        )

        # Create nodes for requirements
        for i, req in enumerate(data.get("requirements", [])):
            req_id = f"req-{spec_id}-{i}"
            nodes.append(
                GraphNode(
                    id=req_id,
                    label=f"Requirement {i + 1}",
                    node_type="requirement",
                    properties={"description": req},
                )
            )
            edges.append(
                GraphEdge(
                    id=f"edge-{spec_id}-{req_id}",
                    source=f"spec-{spec_id}",
                    target=req_id,
                    edge_type="has_requirement",
                )
            )

        # Create nodes for constraints
        for i, constraint in enumerate(data.get("constraints", [])):
            constraint_id = f"constraint-{spec_id}-{i}"
            nodes.append(
                GraphNode(
                    id=constraint_id,
                    label=f"Constraint {i + 1}",
                    node_type="constraint",
                    properties={"description": constraint},
                )
            )
            edges.append(
                GraphEdge(
                    id=f"edge-{spec_id}-{constraint_id}",
                    source=f"spec-{spec_id}",
                    target=constraint_id,
                    edge_type="has_constraint",
                )
            )

        # Create nodes for test cases
        for test in data.get("test_cases", []):
            test_id = f"test-{test['id']}"
            nodes.append(
                GraphNode(
                    id=test_id,
                    label=test.get("name", test["id"]),
                    node_type="test_case",
                    properties={
                        "given": test.get("given"),
                        "when": test.get("when"),
                        "then": test.get("then"),
                    },
                )
            )
            edges.append(
                GraphEdge(
                    id=f"edge-{spec_id}-{test_id}",
                    source=f"spec-{spec_id}",
                    target=test_id,
                    edge_type="has_test_case",
                )
            )

        return KnowledgeGraph(
            id=spec_id,
            name=data.get("title", spec_id),
            description=data.get("purpose", ""),
            nodes=nodes,
            edges=edges,
            metadata={"source": "sovereignspec", "file": str(path)},
        )

    def _import_markdown(self, path: Path) -> KnowledgeGraph:
        """Import a graph from Markdown format."""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        nodes = []
        edges = []

        # Extract headings as concepts
        lines = content.split("\n")
        current_section = None

        for line in lines:
            if line.startswith("# "):
                # Main title
                title = line[2:].strip()
                nodes.append(
                    GraphNode(
                        id=f"concept-{path.stem}",
                        label=title,
                        node_type="concept",
                        properties={"level": 1},
                    )
                )
            elif line.startswith("## "):
                # Section heading
                if current_section:
                    nodes.append(
                        GraphNode(
                            id=f"concept-{current_section}",
                            label=current_section,
                            node_type="concept",
                            properties={"level": 2},
                        )
                    )
                current_section = line[3:].strip().lower().replace(" ", "-")
                nodes.append(
                    GraphNode(
                        id=f"concept-{current_section}",
                        label=line[3:].strip(),
                        node_type="concept",
                        properties={"level": 2},
                    )
                )
                edges.append(
                    GraphEdge(
                        id=f"edge-{path.stem}-{current_section}",
                        source=f"concept-{path.stem}",
                        target=f"concept-{current_section}",
                        edge_type="contains",
                    )
                )

        return KnowledgeGraph(
            id=path.stem,
            name=path.stem,
            description=f"Knowledge graph extracted from {path.name}",
            nodes=nodes,
            edges=edges,
            metadata={"source": "markdown", "file": str(path)},
        )

    def _import_danielkliewer(self, path: Path) -> KnowledgeGraph:
        """Import a graph from DanielKliewer.com format.

        This format has nodes with types (Article, Chunk, Concept, etc.)
        and properties including filename, date, tags, and text content.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        nodes = []
        edges = []

        # Track articles and their chunks for relationship building
        articles = {}
        chunks = {}
        concepts = {}
        projects = {}
        tools = {}
        companies = {}
        libraries = {}
        people = {}
        entities = {}

        for node_data in data.get("nodes", []):
            node_id = node_data["id"]
            node_type = node_data.get("type", "concept")
            label = node_data.get("label", node_id)
            properties = node_data.get("properties", {})

            # Create the node
            node = GraphNode(
                id=node_id,
                label=label,
                node_type=node_type.lower(),
                properties=properties,
            )
            nodes.append(node)

            # Track by type for relationship building
            if node_type == "Article":
                articles[node_id] = node
            elif node_type == "Chunk":
                chunks[node_id] = node
            elif node_type == "Concept":
                concepts[node_id] = node
            elif node_type == "Project":
                projects[node_id] = node
            elif node_type == "Tool":
                tools[node_id] = node
            elif node_type == "Company":
                companies[node_id] = node
            elif node_type == "Library":
                libraries[node_id] = node
            elif node_type == "Person":
                people[node_id] = node
            elif node_type == "Entity":
                entities[node_id] = node

        # Build relationships based on the graph structure
        edge_id_counter = 0

        # Connect chunks to their parent articles
        for chunk_id, chunk in chunks.items():
            chunk_props = chunk.properties
            # Find the article this chunk belongs to
            for article_id, article in articles.items():
                article_props = article.properties
                if article_props.get("filename") and chunk_props.get("text"):
                    # Simple heuristic: if chunk text appears in article context
                    edges.append(
                        GraphEdge(
                            id=f"edge-{edge_id_counter}",
                            source=article_id,
                            target=chunk_id,
                            edge_type="contains",
                            properties={"relationship": "article_contains_chunk"},
                        )
                    )
                    edge_id_counter += 1
                    break

        # Connect concepts to articles based on tags
        for article_id, article in articles.items():
            article_tags = article.properties.get("tags", [])
            for tag in article_tags:
                # Find or create concept for this tag
                concept_id = f"concept-{tag.lower().replace(' ', '-')}"
                if concept_id in concepts:
                    edges.append(
                        GraphEdge(
                            id=f"edge-{edge_id_counter}",
                            source=article_id,
                            target=concept_id,
                            edge_type="discusses",
                            properties={"tag": tag},
                        )
                    )
                    edge_id_counter += 1

        # Connect tools to projects
        for tool_id, tool in tools.items():
            for project_id, project in projects.items():
                # Simple heuristic: if tool name appears in project context
                tool_name = tool.label.lower()
                project_name = project.label.lower()
                if tool_name in project_name or project_name in tool_name:
                    edges.append(
                        GraphEdge(
                            id=f"edge-{edge_id_counter}",
                            source=project_id,
                            target=tool_id,
                            edge_type="uses",
                        )
                    )
                    edge_id_counter += 1

        # Connect libraries to tools
        for library_id, library in libraries.items():
            for tool_id, tool in tools.items():
                library_name = library.label.lower()
                tool_name = tool.label.lower()
                if library_name in tool_name or tool_name in library_name:
                    edges.append(
                        GraphEdge(
                            id=f"edge-{edge_id_counter}",
                            source=tool_id,
                            target=library_id,
                            edge_type="uses",
                        )
                    )
                    edge_id_counter += 1

        # Connect companies to projects
        for company_id, company in companies.items():
            for project_id, project in projects.items():
                company_name = company.label.lower()
                project_name = project.label.lower()
                if company_name in project_name or project_name in company_name:
                    edges.append(
                        GraphEdge(
                            id=f"edge-{edge_id_counter}",
                            source=company_id,
                            target=project_id,
                            edge_type="associated_with",
                        )
                    )
                    edge_id_counter += 1

        # Connect people to articles
        for person_id, person in people.items():
            for article_id, article in articles.items():
                person_name = person.label.lower()
                article_title = article.label.lower()
                if person_name in article_title:
                    edges.append(
                        GraphEdge(
                            id=f"edge-{edge_id_counter}",
                            source=person_id,
                            target=article_id,
                            edge_type="authored",
                        )
                    )
                    edge_id_counter += 1

        # Build metadata
        metadata = {
            "source": "danielkliewer",
            "file": str(path),
            "node_counts": {
                "articles": len(articles),
                "chunks": len(chunks),
                "concepts": len(concepts),
                "projects": len(projects),
                "tools": len(tools),
                "companies": len(companies),
                "libraries": len(libraries),
                "people": len(people),
                "entities": len(entities),
            },
        }

        return KnowledgeGraph(
            id="danielkliewer",
            name="DanielKliewer.com Knowledge Graph",
            description="Knowledge graph extracted from DanielKliewer.com blog posts covering Sovereign AI, Knowledge Graphs, Dynamic Persona MoE RAG, Context Engineering, and Agentic Systems",
            nodes=nodes,
            edges=edges,
            metadata=metadata,
        )