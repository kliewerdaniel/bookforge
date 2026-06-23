"""Review agents for chapter evaluation."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from .base import BaseAgent, AgentConfig, AgentResult
from ..writing.generator import GeneratedChapter


class ReviewIssue(BaseModel):
    """An issue found during review."""

    id: str = Field(..., description="Unique issue identifier")
    severity: str = Field(..., description="Issue severity (critical, major, minor)")
    category: str = Field(..., description="Issue category")
    description: str = Field(..., description="Issue description")
    location: str = Field(default="", description="Issue location in text")
    suggestion: str = Field(default="", description="Suggested fix")


class ReviewReport(BaseModel):
    """Review report for a chapter."""

    id: str = Field(..., description="Unique review identifier")
    chapter_id: str = Field(..., description="Chapter being reviewed")
    reviewer_type: str = Field(..., description="Type of reviewer")
    issues: list[ReviewIssue] = Field(default_factory=list, description="Found issues")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    score: float = Field(default=0.8, description="Quality score (0-1)")
    summary: str = Field(default="", description="Review summary")
    created_at: datetime = Field(default_factory=datetime.now, description="Review timestamp")

    @property
    def issue_count(self) -> int:
        """Get issue count."""
        return len(self.issues)

    @property
    def critical_issues(self) -> int:
        """Get critical issue count."""
        return len([i for i in self.issues if i.severity == "critical"])


class TechnicalReviewer(BaseAgent):
    """Reviews chapters for technical accuracy."""

    def __init__(self):
        super().__init__(
            AgentConfig(
                name="TechnicalReviewer",
                description="Reviews technical accuracy of content",
            )
        )

    def process(self, input_data: GeneratedChapter) -> AgentResult:
        """Review chapter for technical accuracy.

        Args:
            input_data: Chapter to review

        Returns:
            Review result
        """
        if not self.validate_input(input_data):
            return AgentResult(
                agent_name=self.config.name,
                success=False,
                errors=["Invalid input: chapter required"],
            )

        issues = self._check_technical_accuracy(input_data)
        recommendations = self._generate_recommendations(input_data, issues)
        score = self._calculate_score(issues)

        report = ReviewReport(
            id=f"tech-review-{input_data.id}",
            chapter_id=input_data.id,
            reviewer_type="technical",
            issues=issues,
            recommendations=recommendations,
            score=score,
            summary=f"Technical review found {len(issues)} issues",
        )

        return AgentResult(
            agent_name=self.config.name,
            output=report,
            metadata={"issue_count": len(issues), "score": score},
        )

    def _check_technical_accuracy(self, chapter: GeneratedChapter) -> list[ReviewIssue]:
        """Check for technical accuracy issues."""
        issues = []

        # Check for missing citations
        for section in chapter.sections:
            for paragraph in section.paragraphs:
                if not paragraph.citations and len(paragraph.content) > 100:
                    issues.append(
                        ReviewIssue(
                            id=f"issue-{len(issues)}",
                            severity="minor",
                            category="citation",
                            description="Paragraph lacks citations",
                            location=paragraph.id,
                            suggestion="Add citations to support claims",
                        )
                    )

        # Check for unsupported claims
        content = chapter.content.lower()
        claim_words = ["must", "should", "always", "never", "requires"]
        for word in claim_words:
            if word in content:
                # Simple check for claim without citation
                if not chapter.citations:
                    issues.append(
                        ReviewIssue(
                            id=f"issue-{len(issues)}",
                            severity="major",
                            category="evidence",
                            description=f"Found claim '{word}' without supporting evidence",
                            suggestion="Add evidence or soften the claim",
                        )
                    )

        return issues

    def _generate_recommendations(
        self, chapter: GeneratedChapter, issues: list[ReviewIssue]
    ) -> list[str]:
        """Generate recommendations based on issues."""
        recommendations = []

        if issues:
            critical_count = len([i for i in issues if i.severity == "critical"])
            if critical_count > 0:
                recommendations.append(f"Address {critical_count} critical technical issues")

            major_count = len([i for i in issues if i.severity == "major"])
            if major_count > 0:
                recommendations.append(f"Review {major_count} major technical concerns")

        if not chapter.citations:
            recommendations.append("Add citations to support technical claims")

        return recommendations

    def _calculate_score(self, issues: list[ReviewIssue]) -> float:
        """Calculate quality score based on issues."""
        score = 1.0

        for issue in issues:
            if issue.severity == "critical":
                score -= 0.2
            elif issue.severity == "major":
                score -= 0.1
            elif issue.severity == "minor":
                score -= 0.05

        return max(0.0, min(1.0, score))


class EditorialReviewer(BaseAgent):
    """Reviews chapters for editorial quality."""

    def __init__(self):
        super().__init__(
            AgentConfig(
                name="EditorialReviewer",
                description="Reviews editorial quality and readability",
            )
        )

    def process(self, input_data: GeneratedChapter) -> AgentResult:
        """Review chapter for editorial quality.

        Args:
            input_data: Chapter to review

        Returns:
            Review result
        """
        if not self.validate_input(input_data):
            return AgentResult(
                agent_name=self.config.name,
                success=False,
                errors=["Invalid input: chapter required"],
            )

        issues = self._check_editorial_quality(input_data)
        recommendations = self._generate_recommendations(input_data, issues)
        score = self._calculate_score(issues)

        report = ReviewReport(
            id=f"editorial-review-{input_data.id}",
            chapter_id=input_data.id,
            reviewer_type="editorial",
            issues=issues,
            recommendations=recommendations,
            score=score,
            summary=f"Editorial review found {len(issues)} issues",
        )

        return AgentResult(
            agent_name=self.config.name,
            output=report,
            metadata={"issue_count": len(issues), "score": score},
        )

    def _check_editorial_quality(self, chapter: GeneratedChapter) -> list[ReviewIssue]:
        """Check for editorial quality issues."""
        issues = []

        # Check for very long paragraphs
        for section in chapter.sections:
            for paragraph in section.paragraphs:
                word_count = len(paragraph.content.split())
                if word_count > 200:
                    issues.append(
                        ReviewIssue(
                            id=f"issue-{len(issues)}",
                            severity="minor",
                            category="readability",
                            description=f"Paragraph is very long ({word_count} words)",
                            location=paragraph.id,
                            suggestion="Consider splitting into shorter paragraphs",
                        )
                    )

        # Check for repetitive content
        sentences = chapter.content.split(".")
        if len(sentences) > 10:
            unique_sentences = set(s.strip().lower() for s in sentences if s.strip())
            if len(unique_sentences) < len(sentences) * 0.8:
                issues.append(
                    ReviewIssue(
                        id=f"issue-{len(issues)}",
                        severity="major",
                        category="originality",
                        description="Content appears repetitive",
                        suggestion="Add more variety to the content",
                    )
                )

        return issues

    def _generate_recommendations(
        self, chapter: GeneratedChapter, issues: list[ReviewIssue]
    ) -> list[str]:
        """Generate recommendations based on issues."""
        recommendations = []

        if issues:
            recommendations.append("Address editorial issues to improve readability")

        if chapter.word_count < 1000:
            recommendations.append("Consider expanding the chapter for better coverage")

        return recommendations

    def _calculate_score(self, issues: list[ReviewIssue]) -> float:
        """Calculate quality score based on issues."""
        score = 1.0

        for issue in issues:
            if issue.severity == "critical":
                score -= 0.2
            elif issue.severity == "major":
                score -= 0.1
            elif issue.severity == "minor":
                score -= 0.05

        return max(0.0, min(1.0, score))


class CitationReviewer(BaseAgent):
    """Reviews chapters for citation quality."""

    def __init__(self):
        super().__init__(
            AgentConfig(
                name="CitationReviewer",
                description="Reviews citation quality and completeness",
            )
        )

    def process(self, input_data: GeneratedChapter) -> AgentResult:
        """Review chapter for citation quality.

        Args:
            input_data: Chapter to review

        Returns:
            Review result
        """
        if not self.validate_input(input_data):
            return AgentResult(
                agent_name=self.config.name,
                success=False,
                errors=["Invalid input: chapter required"],
            )

        issues = self._check_citation_quality(input_data)
        recommendations = self._generate_recommendations(input_data, issues)
        score = self._calculate_score(issues)

        report = ReviewReport(
            id=f"citation-review-{input_data.id}",
            chapter_id=input_data.id,
            reviewer_type="citation",
            issues=issues,
            recommendations=recommendations,
            score=score,
            summary=f"Citation review found {len(issues)} issues",
        )

        return AgentResult(
            agent_name=self.config.name,
            output=report,
            metadata={"issue_count": len(issues), "score": score},
        )

    def _check_citation_quality(self, chapter: GeneratedChapter) -> list[ReviewIssue]:
        """Check for citation quality issues."""
        issues = []

        # Check for missing citations
        if not chapter.citations:
            issues.append(
                ReviewIssue(
                    id="issue-0",
                    severity="major",
                    category="citation",
                    description="Chapter has no citations",
                    suggestion="Add citations to support claims",
                )
            )

        # Check for uncited claims
        for section in chapter.sections:
            for paragraph in section.paragraphs:
                if not paragraph.citations and len(paragraph.content) > 50:
                    issues.append(
                        ReviewIssue(
                            id=f"issue-{len(issues)}",
                            severity="minor",
                            category="citation",
                            description="Paragraph has no citations",
                            location=paragraph.id,
                            suggestion="Add citations to support claims",
                        )
                    )

        return issues

    def _generate_recommendations(
        self, chapter: GeneratedChapter, issues: list[ReviewIssue]
    ) -> list[str]:
        """Generate recommendations based on issues."""
        recommendations = []

        if not chapter.citations:
            recommendations.append("Add citations to support technical claims")

        uncited_count = len([i for i in issues if i.category == "citation"])
        if uncited_count > 0:
            recommendations.append(f"Add citations to {uncited_count} paragraphs")

        return recommendations

    def _calculate_score(self, issues: list[ReviewIssue]) -> float:
        """Calculate quality score based on issues."""
        score = 1.0

        for issue in issues:
            if issue.severity == "critical":
                score -= 0.2
            elif issue.severity == "major":
                score -= 0.1
            elif issue.severity == "minor":
                score -= 0.05

        return max(0.0, min(1.0, score))