"""Evidence collector for gathering supporting sources."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class EvidenceSource(BaseModel):
    """A source of evidence."""

    id: str = Field(..., description="Unique source identifier")
    title: str = Field(..., description="Source title")
    source_type: str = Field(..., description="Source type (graph, document, paper, etc.)")
    url: str | None = Field(default=None, description="Source URL")
    content: str = Field(default="", description="Source content or excerpt")
    reliability: float = Field(default=0.8, description="Source reliability score (0-1)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Source metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Collection timestamp")


class EvidenceItem(BaseModel):
    """A piece of evidence supporting a claim."""

    id: str = Field(..., description="Unique evidence identifier")
    claim: str = Field(..., description="The claim being supported")
    sources: list[EvidenceSource] = Field(default_factory=list, description="Supporting sources")
    confidence: float = Field(default=0.8, description="Confidence score (0-1)")
    provenance: dict[str, Any] = Field(default_factory=dict, description="Provenance tracking")
    created_at: datetime = Field(default_factory=datetime.now, description="Collection timestamp")


class EvidenceMap(BaseModel):
    """Map of evidence for a chapter or section."""

    id: str = Field(..., description="Unique evidence map identifier")
    paragraph_id: str = Field(..., description="Paragraph or section identifier")
    items: list[EvidenceItem] = Field(default_factory=list, description="Evidence items")
    total_confidence: float = Field(default=0.0, description="Overall confidence score")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    def calculate_confidence(self) -> float:
        """Calculate total confidence based on evidence items."""
        if not self.items:
            return 0.0

        total = sum(item.confidence for item in self.items)
        self.total_confidence = total / len(self.items)
        return self.total_confidence


class EvidenceCollector:
    """Collects and organizes evidence for content generation."""

    def __init__(self):
        self.sources: list[EvidenceSource] = []
        self.evidence_maps: list[EvidenceMap] = []

    def add_source(self, source: EvidenceSource) -> None:
        """Add an evidence source."""
        self.sources.append(source)

    def collect_evidence(
        self,
        claim: str,
        context: dict[str, Any] | None = None,
    ) -> EvidenceItem:
        """Collect evidence for a specific claim.

        Args:
            claim: The claim to find evidence for
            context: Additional context for evidence collection

        Returns:
            Evidence item with supporting sources
        """
        # Find relevant sources
        relevant_sources = self._find_relevant_sources(claim, context)

        # Calculate confidence
        confidence = self._calculate_confidence(relevant_sources)

        # Create evidence item
        evidence = EvidenceItem(
            id=f"evidence-{len(self.sources)}",
            claim=claim,
            sources=relevant_sources,
            confidence=confidence,
            provenance={
                "claim": claim,
                "source_count": len(relevant_sources),
                "context": context or {},
            },
        )

        return evidence

    def create_evidence_map(
        self,
        paragraph_id: str,
        claims: list[str],
        context: dict[str, Any] | None = None,
    ) -> EvidenceMap:
        """Create an evidence map for a paragraph or section.

        Args:
            paragraph_id: The paragraph or section identifier
            claims: List of claims to find evidence for
            context: Additional context

        Returns:
            Complete evidence map
        """
        items = []
        for claim in claims:
            evidence = self.collect_evidence(claim, context)
            items.append(evidence)

        evidence_map = EvidenceMap(
            id=f"emap-{paragraph_id}",
            paragraph_id=paragraph_id,
            items=items,
        )
        evidence_map.calculate_confidence()

        self.evidence_maps.append(evidence_map)
        return evidence_map

    def _find_relevant_sources(
        self,
        claim: str,
        context: dict[str, Any] | None = None,
    ) -> list[EvidenceSource]:
        """Find sources relevant to a claim."""
        # Simple keyword matching for now
        claim_words = set(claim.lower().split())
        relevant = []

        for source in self.sources:
            # Calculate relevance based on word overlap
            source_words = set(source.content.lower().split())
            overlap = len(claim_words & source_words)
            if overlap > 0:
                relevant.append(source)

        # Sort by reliability
        relevant.sort(key=lambda s: s.reliability, reverse=True)

        return relevant[:5]  # Return top 5 sources

    def _calculate_confidence(self, sources: list[EvidenceSource]) -> float:
        """Calculate confidence score based on sources."""
        if not sources:
            return 0.0

        # Average reliability with diminishing returns
        reliabilities = [s.reliability for s in sources]
        avg_reliability = sum(reliabilities) / len(reliabilities)

        # Bonus for multiple sources
        source_bonus = min(0.2, len(sources) * 0.05)

        return min(1.0, avg_reliability + source_bonus)