"""Artifact storage for persisting intermediate results."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    """An artifact produced by the pipeline."""

    id: str = Field(..., description="Unique artifact identifier")
    artifact_type: str = Field(..., description="Artifact type (graph, survey, theme, etc.)")
    file_path: str = Field(..., description="File path where artifact is stored")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Artifact metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class ArtifactStorage:
    """Stores and retrieves pipeline artifacts."""

    def __init__(self, base_dir: str = ".bookforge"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts: list[Artifact] = []

        # Create subdirectories
        (self.base_dir / "graphs").mkdir(exist_ok=True)
        (self.base_dir / "surveys").mkdir(exist_ok=True)
        (self.base_dir / "themes").mkdir(exist_ok=True)
        (self.base_dir / "blueprints").mkdir(exist_ok=True)
        (self.base_dir / "chapters").mkdir(exist_ok=True)
        (self.base_dir / "reviews").mkdir(exist_ok=True)
        (self.base_dir / "output").mkdir(exist_ok=True)

    def save_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        data: Any,
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:
        """Save an artifact to disk.

        Args:
            artifact_id: Unique artifact identifier
            artifact_type: Type of artifact
            data: Artifact data (must be JSON-serializable)
            metadata: Optional metadata

        Returns:
            Saved artifact
        """
        # Determine file path
        file_path = self.base_dir / artifact_type / f"{artifact_id}.json"

        # Save data
        with open(file_path, "w", encoding="utf-8") as f:
            if hasattr(data, "model_dump"):
                json.dump(data.model_dump(), f, indent=2, default=str)
            elif isinstance(data, dict):
                json.dump(data, f, indent=2, default=str)
            else:
                json.dump({"data": str(data)}, f, indent=2)

        # Create artifact record
        artifact = Artifact(
            id=artifact_id,
            artifact_type=artifact_type,
            file_path=str(file_path),
            metadata=metadata or {},
        )
        self.artifacts.append(artifact)

        return artifact

    def load_artifact(self, artifact_id: str, artifact_type: str) -> Any:
        """Load an artifact from disk.

        Args:
            artifact_id: Artifact identifier
            artifact_type: Type of artifact

        Returns:
            Loaded artifact data
        """
        file_path = self.base_dir / artifact_type / f"{artifact_id}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Artifact not found: {artifact_id}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_artifacts(self, artifact_type: str | None = None) -> list[Artifact]:
        """List stored artifacts.

        Args:
            artifact_type: Optional filter by type

        Returns:
            List of artifacts
        """
        if artifact_type:
            return [a for a in self.artifacts if a.artifact_type == artifact_type]
        return self.artifacts

    def get_artifact_path(self, artifact_id: str, artifact_type: str) -> Path:
        """Get the file path for an artifact.

        Args:
            artifact_id: Artifact identifier
            artifact_type: Type of artifact

        Returns:
            File path
        """
        return self.base_dir / artifact_type / f"{artifact_id}.json"