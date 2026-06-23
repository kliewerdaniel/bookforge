"""Research layer for gap identification and evidence collection."""

from .evidence import EvidenceCollector, EvidenceMap, EvidenceSource
from .gaps import GapAnalyzer, KnowledgeGap

__all__ = ["EvidenceCollector", "EvidenceMap", "EvidenceSource", "GapAnalyzer", "KnowledgeGap"]