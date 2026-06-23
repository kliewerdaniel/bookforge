"""API routes for BookForge."""

from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..knowledge.importer import GraphImporter
from ..knowledge.analyzer import GraphAnalyzer
from ..research.evidence import EvidenceCollector, EvidenceSource
from ..research.gaps import GapAnalyzer
from ..planning.themes import ThemeConstructor
from ..planning.blueprint import BlueprintGenerator
from ..writing.generator import ChapterGenerator
from ..writing.evidence_writing import EvidenceBackedWriter
from ..publishing.compiler import BookCompiler
from ..agents.reviewer import TechnicalReviewer, EditorialReviewer, CitationReviewer

router = APIRouter()

# Initialize components
importer = GraphImporter()
analyzer = GraphAnalyzer()
evidence_collector = EvidenceCollector()
gap_analyzer = GapAnalyzer()
theme_constructor = ThemeConstructor()
blueprint_generator = BlueprintGenerator()
chapter_generator = ChapterGenerator()
evidence_writer = EvidenceBackedWriter(evidence_collector)
book_compiler = BookCompiler()

# Reviewers
technical_reviewer = TechnicalReviewer()
editorial_reviewer = EditorialReviewer()
citation_reviewer = CitationReviewer()


class GraphImportRequest(BaseModel):
    """Request to import a knowledge graph."""

    graph_path: str = Field(..., description="Path to the graph file")
    format: str = Field(default="auto", description="Graph format")


class GraphImportResponse(BaseModel):
    """Response from graph import."""

    graph_id: str
    node_count: int
    edge_count: int
    name: str


class SurveyResponse(BaseModel):
    """Response from survey."""

    survey_id: str
    concepts: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    gaps: list[dict[str, Any]]


class ThemeResponse(BaseModel):
    """Response from theme construction."""

    theme_id: str
    themes: list[dict[str, Any]]
    concept_groups: list[list[str]]


class BlueprintResponse(BaseModel):
    """Response from blueprint generation."""

    blueprint_id: str
    parts: list[dict[str, Any]]
    chapters: list[dict[str, Any]]
    learning_objectives: list[dict[str, Any]]


class ChapterSpecResponse(BaseModel):
    """Response from chapter specification."""

    chapter_specs: list[dict[str, Any]]
    evidence_maps: list[dict[str, Any]]
    illustration_specs: list[dict[str, Any]]


class GenerateRequest(BaseModel):
    """Request to generate a chapter."""

    chapter_id: str = Field(..., description="Chapter specification ID")


class GenerateResponse(BaseModel):
    """Response from chapter generation."""

    draft_id: str
    content: str
    word_count: int
    citations: list[str]


class ReviewRequest(BaseModel):
    """Request to review a chapter."""

    chapter_id: str = Field(..., description="Chapter ID to review")
    review_type: str = Field(..., description="Review type (technical, editorial, citation)")


class ReviewResponse(BaseModel):
    """Response from review."""

    review_id: str
    issues: list[dict[str, Any]]
    recommendations: list[str]
    score: float


class CompileRequest(BaseModel):
    """Request to compile a book."""

    book_id: str = Field(..., description="Book ID to compile")
    formats: list[str] = Field(..., description="Output formats (pdf, epub, html)")


class CompileResponse(BaseModel):
    """Response from compilation."""

    compilation_id: str
    outputs: list[dict[str, Any]]
    file_paths: list[str]


# Store for imported graphs and generated artifacts
graphs: dict[str, Any] = {}
surveys: dict[str, Any] = {}
themes: dict[str, Any] = {}
blueprints: dict[str, Any] = {}
chapters: dict[str, Any] = {}
reviews: dict[str, Any] = {}


@router.post("/api/graph/import", response_model=GraphImportResponse)
async def import_graph(request: GraphImportRequest):
    """Import a knowledge graph."""
    try:
        graph = importer.import_graph(request.graph_path, request.format)
        graphs[graph.id] = graph

        return GraphImportResponse(
            graph_id=graph.id,
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            name=graph.name,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/survey/{graph_id}", response_model=SurveyResponse)
async def survey_graph(graph_id: str):
    """Perform semantic survey of a knowledge graph."""
    if graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph not found")

    graph = graphs[graph_id]
    survey_result = analyzer.survey(graph)
    surveys[graph_id] = survey_result

    return SurveyResponse(
        survey_id=f"survey-{graph_id}",
        concepts=[
            {
                "id": c.id,
                "label": c.label,
                "frequency": c.frequency,
                "centrality": c.centrality,
            }
            for c in survey_result.concepts
        ],
        relationships=[
            {
                "source": r.source,
                "target": r.target,
                "type": r.relationship_type,
                "strength": r.strength,
            }
            for r in survey_result.relationships
        ],
        gaps=[
            {
                "topic": g.topic,
                "description": g.description,
                "importance": g.importance,
            }
            for g in survey_result.gaps
        ],
    )


@router.post("/api/themes/{survey_id}", response_model=ThemeResponse)
async def construct_themes(survey_id: str):
    """Construct themes from survey results."""
    graph_id = survey_id.replace("survey-", "")
    if graph_id not in surveys:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey = surveys[graph_id]
    graph = graphs[graph_id]
    theme_graph = theme_constructor.construct_themes(survey, graph)
    themes[graph_id] = theme_graph

    return ThemeResponse(
        theme_id=theme_graph.id,
        themes=[
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "concept_count": len(t.concepts),
            }
            for t in theme_graph.themes
        ],
        concept_groups=[t.concepts for t in theme_graph.themes],
    )


@router.post("/api/blueprint/{theme_id}", response_model=BlueprintResponse)
async def generate_blueprint(theme_id: str, title: str = "Untitled Book"):
    """Generate book blueprint from themes."""
    graph_id = theme_id.replace("themes-", "")
    if graph_id not in themes:
        raise HTTPException(status_code=404, detail="Themes not found")

    theme_graph = themes[graph_id]
    blueprint = blueprint_generator.generate(theme_graph, title=title)
    blueprints[graph_id] = blueprint

    return BlueprintResponse(
        blueprint_id=blueprint.id,
        parts=[
            {
                "id": p.id,
                "title": p.title,
                "chapter_count": len(p.chapters),
            }
            for p in blueprint.parts
        ],
        chapters=[
            {
                "id": c.id,
                "title": c.title,
                "word_count_target": c.word_count_target,
            }
            for c in blueprint.chapters
        ],
        learning_objectives=[
            {
                "id": o.id,
                "description": o.description,
            }
            for o in blueprint.learning_objectives
        ],
    )


@router.post("/api/chapters/{blueprint_id}", response_model=ChapterSpecResponse)
async def generate_chapter_specs(blueprint_id: str):
    """Generate chapter specifications from blueprint."""
    graph_id = blueprint_id.replace("blueprint-", "")
    if graph_id not in blueprints:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    blueprint = blueprints[graph_id]

    return ChapterSpecResponse(
        chapter_specs=[
            {
                "id": c.id,
                "title": c.title,
                "theme_id": c.theme_id,
                "word_count_target": c.word_count_target,
            }
            for c in blueprint.chapters
        ],
        evidence_maps=[],
        illustration_specs=[],
    )


@router.post("/api/generate/{chapter_id}", response_model=GenerateResponse)
async def generate_chapter(chapter_id: str):
    """Generate chapter content."""
    # Find the chapter spec
    chapter_spec = None
    for blueprint in blueprints.values():
        for spec in blueprint.chapters:
            if spec.id == chapter_id:
                chapter_spec = spec
                break

    if not chapter_spec:
        raise HTTPException(status_code=404, detail="Chapter specification not found")

    # Generate chapter
    chapter = chapter_generator.generate_chapter(chapter_spec)
    chapters[chapter_id] = chapter

    return GenerateResponse(
        draft_id=chapter.id,
        content=chapter.content,
        word_count=chapter.word_count,
        citations=chapter.citations,
    )


@router.post("/api/review/{draft_id}", response_model=ReviewResponse)
async def review_chapter(draft_id: str, review_type: str = "technical"):
    """Review a generated chapter."""
    if draft_id not in chapters:
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter = chapters[draft_id]

    # Select reviewer
    if review_type == "technical":
        reviewer = technical_reviewer
    elif review_type == "editorial":
        reviewer = editorial_reviewer
    elif review_type == "citation":
        reviewer = citation_reviewer
    else:
        raise HTTPException(status_code=400, detail="Invalid review type")

    # Perform review
    result = reviewer.process(chapter)
    report = result.output
    reviews[report.id] = report

    return ReviewResponse(
        review_id=report.id,
        issues=[
            {
                "id": i.id,
                "severity": i.severity,
                "category": i.category,
                "description": i.description,
            }
            for i in report.issues
        ],
        recommendations=report.recommendations,
        score=report.score,
    )


@router.post("/api/compile/{book_id}", response_model=CompileResponse)
async def compile_book(book_id: str, formats: list[str] = ["html"]):
    """Compile a book to multiple formats."""
    # Find the blueprint
    blueprint = None
    for bid, bp in blueprints.items():
        if bp.id == book_id:
            blueprint = bp
            break

    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    # Get all chapters for this blueprint
    book_chapters = []
    for chapter in chapters.values():
        if any(c.id == chapter.id for c in blueprint.chapters):
            book_chapters.append(chapter)

    # Compile
    compiled = book_compiler.compile(blueprint, book_chapters, formats)

    return CompileResponse(
        compilation_id=compiled.id,
        outputs=[
            {"format": fmt, "path": path}
            for fmt, path in compiled.formats.items()
        ],
        file_paths=list(compiled.formats.values()),
    )