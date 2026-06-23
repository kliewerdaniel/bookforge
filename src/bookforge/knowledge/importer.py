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