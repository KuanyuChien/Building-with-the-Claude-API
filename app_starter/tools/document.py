from pathlib import Path

from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pydantic import Field

SUPPORTED_EXTENSIONS = {"pdf", "docx"}


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    path: str = Field(description="Path to the PDF or DOCX file to convert to markdown"),
) -> str:
    """Convert a PDF or DOCX file on disk to markdown-formatted text.

    Reads the file at the given path and converts its contents to markdown,
    inferring the document type from the file's extension (.pdf or .docx,
    case-insensitive). Raises a ValueError if the extension isn't one of the
    supported types.

    When to use:
    - When you have a local file path to a PDF or DOCX document and want its
      contents as markdown text
    - When you don't already have the document's bytes in memory (otherwise
      use `binary_document_to_markdown` directly)

    Examples:
    >>> document_path_to_markdown("report.pdf")  # doctest: +SKIP
    '# Report\\n\\nThis is the report content...'
    """
    file_path = Path(path)
    extension = file_path.suffix.lstrip(".").lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{extension or '(none)'}' for '{path}'. "
            f"Expected one of: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    with open(file_path, "rb") as f:
        binary_data = f.read()

    return binary_document_to_markdown(binary_data, extension)
