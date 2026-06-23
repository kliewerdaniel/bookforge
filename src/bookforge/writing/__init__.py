"""Writing layer for content generation with evidence backing."""

from .generator import ChapterGenerator, GeneratedChapter
from .evidence_writing import EvidenceBackedWriter

__all__ = ["ChapterGenerator", "GeneratedChapter", "EvidenceBackedWriter"]