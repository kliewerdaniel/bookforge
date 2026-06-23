"""Format-specific compilers for PDF, EPUB, and HTML output."""

from pathlib import Path
from typing import Any

from ..writing.generator import GeneratedChapter


class PDFCompiler:
    """Compiles chapters to PDF format."""

    def compile(
        self,
        title: str,
        chapters: list[GeneratedChapter],
        output_path: Path,
    ) -> None:
        """Compile chapters to PDF.

        Args:
            title: Book title
            chapters: List of generated chapters
            output_path: Output file path
        """
        # Create PDF content
        content = self._create_pdf_content(title, chapters)

        # Write PDF (simplified - in production, use weasyprint or reportlab)
        with open(output_path.with_suffix(".md"), "w", encoding="utf-8") as f:
            f.write(content)

    def _create_pdf_content(
        self, title: str, chapters: list[GeneratedChapter]
    ) -> str:
        """Create content for PDF."""
        lines = [f"# {title}", ""]

        for chapter in chapters:
            lines.append(chapter.content)
            lines.append("")

        return "\n".join(lines)


class EPUBCompiler:
    """Compiles chapters to EPUB format."""

    def compile(
        self,
        title: str,
        chapters: list[GeneratedChapter],
        output_path: Path,
    ) -> None:
        """Compile chapters to EPUB.

        Args:
            title: Book title
            chapters: List of generated chapters
            output_path: Output file path
        """
        # Create EPUB structure
        content = self._create_epub_content(title, chapters)

        # Write EPUB (simplified - in production, use ebooklib)
        with open(output_path.with_suffix(".html"), "w", encoding="utf-8") as f:
            f.write(content)

    def _create_epub_content(
        self, title: str, chapters: list[GeneratedChapter]
    ) -> str:
        """Create content for EPUB."""
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{title}</title>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>",
        ]

        for chapter in chapters:
            lines.append(chapter.content)

        lines.extend(["</body>", "</html>"])

        return "\n".join(lines)


class HTMLCompiler:
    """Compiles chapters to HTML format."""

    def compile(
        self,
        title: str,
        chapters: list[GeneratedChapter],
        output_path: Path,
    ) -> None:
        """Compile chapters to HTML.

        Args:
            title: Book title
            chapters: List of generated chapters
            output_path: Output file path
        """
        # Create HTML content
        content = self._create_html_content(title, chapters)

        # Write HTML
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_html_content(
        self, title: str, chapters: list[GeneratedChapter]
    ) -> str:
        """Create HTML content."""
        lines = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"<title>{title}</title>",
            "<style>",
            "body { font-family: serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "h1 { text-align: center; }",
            "h2 { border-bottom: 1px solid #ccc; padding-bottom: 5px; }",
            "p { line-height: 1.6; }",
            ".chapter { margin-bottom: 40px; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>",
        ]

        for chapter in chapters:
            lines.append(f"<div class='chapter'>")
            lines.append(chapter.content)
            lines.append("</div>")

        lines.extend(["</body>", "</html>"])

        return "\n".join(lines)