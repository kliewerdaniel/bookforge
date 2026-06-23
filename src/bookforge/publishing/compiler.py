"""Book compiler for multi-format output."""

from datetime import datetime
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from ..writing.generator import GeneratedChapter
from ..planning.blueprint import BookBlueprint
from .formats import PDFCompiler, EPUBCompiler, HTMLCompiler


class CompiledBook(BaseModel):
    """A compiled book in multiple formats."""

    id: str = Field(..., description="Unique compilation identifier")
    title: str = Field(..., description="Book title")
    chapters: list[GeneratedChapter] = Field(default_factory=list, description="Book chapters")
    formats: dict[str, str] = Field(default_factory=dict, description="Format to file path mapping")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Compilation metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Compilation timestamp")

    @property
    def total_word_count(self) -> int:
        """Get total word count."""
        return sum(chapter.word_count for chapter in self.chapters)

    @property
    def chapter_count(self) -> int:
        """Get chapter count."""
        return len(self.chapters)


class BookCompiler:
    """Compiles books into multiple formats."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.pdf_compiler = PDFCompiler()
        self.epub_compiler = EPUBCompiler()
        self.html_compiler = HTMLCompiler()

    def compile(
        self,
        blueprint: BookBlueprint,
        chapters: list[GeneratedChapter],
        formats: list[str],
        title: str | None = None,
    ) -> CompiledBook:
        """Compile a book into specified formats.

        Args:
            blueprint: Book blueprint
            chapters: Generated chapters
            formats: List of output formats (pdf, epub, html)
            title: Book title (uses blueprint title if not provided)

        Returns:
            Compiled book with file paths
        """
        book_title = title or blueprint.title
        book_id = f"book-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Sort chapters by order
        sorted_chapters = sorted(chapters, key=lambda c: c.metadata.get("order", 0))

        # Compile to each format
        compiled_formats = {}

        for fmt in formats:
            if fmt == "pdf":
                output_path = self._compile_pdf(book_id, book_title, sorted_chapters)
                compiled_formats["pdf"] = str(output_path)
            elif fmt == "epub":
                output_path = self._compile_epub(book_id, book_title, sorted_chapters)
                compiled_formats["epub"] = str(output_path)
            elif fmt == "html":
                output_path = self._compile_html(book_id, book_title, sorted_chapters)
                compiled_formats["html"] = str(output_path)

        return CompiledBook(
            id=book_id,
            title=book_title,
            chapters=sorted_chapters,
            formats=compiled_formats,
            metadata={
                "blueprint_id": blueprint.id,
                "chapter_count": len(sorted_chapters),
                "total_word_count": sum(c.word_count for c in sorted_chapters),
                "formats": formats,
            },
        )

    def _compile_pdf(
        self, book_id: str, title: str, chapters: list[GeneratedChapter]
    ) -> Path:
        """Compile book to PDF format."""
        output_path = self.output_dir / f"{book_id}.pdf"
        self.pdf_compiler.compile(title, chapters, output_path)
        return output_path

    def _compile_epub(
        self, book_id: str, title: str, chapters: list[GeneratedChapter]
    ) -> Path:
        """Compile book to EPUB format."""
        output_path = self.output_dir / f"{book_id}.epub"
        self.epub_compiler.compile(title, chapters, output_path)
        return output_path

    def _compile_html(
        self, book_id: str, title: str, chapters: list[GeneratedChapter]
    ) -> Path:
        """Compile book to HTML format."""
        output_path = self.output_dir / f"{book_id}.html"
        self.html_compiler.compile(title, chapters, output_path)
        return output_path