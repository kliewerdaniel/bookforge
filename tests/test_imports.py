"""Simple test to verify package imports."""

def test_import_bookforge():
    """Test that bookforge package can be imported."""
    import bookforge
    assert bookforge.__version__ == "0.1.0"


def test_import_knowledge():
    """Test that knowledge module can be imported."""
    from bookforge.knowledge import KnowledgeGraph, GraphNode, GraphEdge
    assert KnowledgeGraph is not None


def test_import_research():
    """Test that research module can be imported."""
    from bookforge.research import EvidenceCollector, GapAnalyzer
    assert EvidenceCollector is not None


def test_import_planning():
    """Test that planning module can be imported."""
    from bookforge.planning import ThemeConstructor, BlueprintGenerator
    assert ThemeConstructor is not None


def test_import_writing():
    """Test that writing module can be imported."""
    from bookforge.writing import ChapterGenerator, EvidenceBackedWriter
    assert ChapterGenerator is not None


def test_import_publishing():
    """Test that publishing module can be imported."""
    from bookforge.publishing import BookCompiler
    assert BookCompiler is not None


def test_import_agents():
    """Test that agents module can be imported."""
    from bookforge.agents import TechnicalReviewer, EditorialReviewer
    assert TechnicalReviewer is not None


def test_import_api():
    """Test that API module can be imported."""
    from bookforge.api import app
    assert app is not None