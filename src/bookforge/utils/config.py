"""Configuration settings for BookForge."""

from pathlib import Path
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """BookForge settings."""

    # Project settings
    project_name: str = Field(default="bookforge", description="Project name")
    version: str = Field(default="0.1.0", description="BookForge version")

    # Storage settings
    base_dir: str = Field(default=".bookforge", description="Base directory for artifacts")
    output_dir: str = Field(default="output", description="Output directory for compiled books")

    # LLM settings
    model: str = Field(default="qwen2.5-coder:32b", description="LLM model for generation")
    temperature: float = Field(default=0.7, description="Generation temperature")
    max_tokens: int = Field(default=4096, description="Maximum tokens for generation")

    # Pipeline settings
    max_chapters: int = Field(default=20, description="Maximum chapters per book")
    max_words_per_chapter: int = Field(default=10000, description="Maximum words per chapter")
    enable_illustrations: bool = Field(default=True, description="Enable illustration generation")

    # Review settings
    enable_technical_review: bool = Field(default=True, description="Enable technical review")
    enable_editorial_review: bool = Field(default=True, description="Enable editorial review")
    enable_citation_review: bool = Field(default=True, description="Enable citation review")
    min_review_score: float = Field(default=0.7, description="Minimum review score to proceed")

    # Output formats
    output_formats: list[str] = Field(
        default=["html", "pdf", "epub"],
        description="Output formats to generate",
    )

    def get_base_path(self) -> Path:
        """Get the base directory path."""
        return Path(self.base_dir)

    def get_output_path(self) -> Path:
        """Get the output directory path."""
        return Path(self.output_dir)