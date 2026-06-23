"""Tests for graph importer."""

import json
import pytest
from pathlib import Path
from bookforge.knowledge.importer import GraphImporter


class TestGraphImporter:
    """Tests for GraphImporter."""

    def test_import_json_graph(self, tmp_path):
        """Test importing a JSON graph."""
        # Create test JSON graph
        graph_data = {
            "id": "test-graph",
            "name": "Test Graph",
            "nodes": [
                {"id": "n1", "label": "Node 1", "type": "concept"},
                {"id": "n2", "label": "Node 2", "type": "concept"},
            ],
            "edges": [
                {"source": "n1", "target": "n2", "type": "related_to"},
            ],
        }

        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(graph_data))

        # Import graph
        importer = GraphImporter()
        graph = importer.import_graph(str(json_file))

        assert graph.id == "test-graph"
        assert graph.name == "Test Graph"
        assert graph.node_count == 2
        assert graph.edge_count == 1

    def test_detect_format_json(self, tmp_path):
        """Test format detection for JSON files."""
        json_file = tmp_path / "test.json"
        json_file.write_text("{}")

        importer = GraphImporter()
        format = importer._detect_format(json_file)
        assert format == "json"

    def test_detect_format_yaml(self, tmp_path):
        """Test format detection for YAML files."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("id: test")

        importer = GraphImporter()
        format = importer._detect_format(yaml_file)
        assert format == "yaml"

    def test_import_nonexistent_file(self):
        """Test importing a non-existent file."""
        importer = GraphImporter()
        with pytest.raises(FileNotFoundError):
            importer.import_graph("/nonexistent/path.json")