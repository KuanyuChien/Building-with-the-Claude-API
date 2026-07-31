import os
import shutil
from pathlib import Path

import pytest
from tools.document import binary_document_to_markdown, document_path_to_markdown


class TestBinaryDocumentToMarkdown:
    # Define fixture paths
    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")
    PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")

    def test_fixture_files_exist(self):
        """Verify test fixtures exist."""
        assert os.path.exists(self.DOCX_FIXTURE), (
            f"DOCX fixture not found at {self.DOCX_FIXTURE}"
        )
        assert os.path.exists(self.PDF_FIXTURE), (
            f"PDF fixture not found at {self.PDF_FIXTURE}"
        )

    def test_binary_document_to_markdown_with_docx(self):
        """Test converting a DOCX document to markdown."""
        # Read binary content from the fixture
        with open(self.DOCX_FIXTURE, "rb") as f:
            docx_data = f.read()

        # Call function
        result = binary_document_to_markdown(docx_data, "docx")

        # Basic assertions to check the conversion was successful
        assert isinstance(result, str)
        assert len(result) > 0
        # Check for typical markdown formatting - this will depend on your actual test file
        assert "#" in result or "-" in result or "*" in result

    def test_binary_document_to_markdown_with_pdf(self):
        """Test converting a PDF document to markdown."""
        # Read binary content from the fixture
        with open(self.PDF_FIXTURE, "rb") as f:
            pdf_data = f.read()

        # Call function
        result = binary_document_to_markdown(pdf_data, "pdf")

        # Basic assertions to check the conversion was successful
        assert isinstance(result, str)
        assert len(result) > 0
        # Check for typical markdown formatting - this will depend on your actual test file
        assert "#" in result or "-" in result or "*" in result


class TestDocumentPathToMarkdown:
    # Define fixture paths
    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")
    PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")

    def test_document_path_to_markdown_with_pdf(self):
        """Test converting a PDF document to markdown from a file path."""
        result = document_path_to_markdown(self.PDF_FIXTURE)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result or "-" in result or "*" in result

    def test_document_path_to_markdown_with_docx(self):
        """Test converting a DOCX document to markdown from a file path."""
        result = document_path_to_markdown(self.DOCX_FIXTURE)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result or "-" in result or "*" in result

    @pytest.mark.parametrize(
        "path, file_type",
        [(PDF_FIXTURE, "pdf"), (DOCX_FIXTURE, "docx")],
    )
    def test_document_path_to_markdown_matches_binary_conversion(self, path, file_type):
        """Path-based conversion should produce identical output to the binary-based tool."""
        with open(path, "rb") as f:
            binary_result = binary_document_to_markdown(f.read(), file_type)

        path_result = document_path_to_markdown(path)

        assert path_result == binary_result

    def test_document_path_to_markdown_accepts_str_and_pathlib_path(self):
        """The tool should accept both plain strings and pathlib.Path objects."""
        str_result = document_path_to_markdown(self.PDF_FIXTURE)
        path_result = document_path_to_markdown(Path(self.PDF_FIXTURE))

        assert str_result == path_result

    def test_document_path_to_markdown_relative_and_absolute_paths(self, monkeypatch):
        """Conversion should succeed whether given a relative or absolute path."""
        absolute_result = document_path_to_markdown(os.path.abspath(self.PDF_FIXTURE))

        monkeypatch.chdir(self.FIXTURES_DIR)
        relative_result = document_path_to_markdown("mcp_docs.pdf")

        assert absolute_result == relative_result

    def test_document_path_to_markdown_infers_type_from_extension(self, tmp_path):
        """The file type used for conversion should be inferred from the path's extension."""
        pdf_copy = tmp_path / "copy.pdf"
        shutil.copyfile(self.PDF_FIXTURE, pdf_copy)

        result = document_path_to_markdown(str(pdf_copy))

        with open(self.PDF_FIXTURE, "rb") as f:
            expected = binary_document_to_markdown(f.read(), "pdf")

        assert result == expected

    def test_document_path_to_markdown_with_uppercase_extension(self, tmp_path):
        """Extension matching should be case-insensitive (e.g. REPORT.PDF)."""
        pdf_copy = tmp_path / "REPORT.PDF"
        shutil.copyfile(self.PDF_FIXTURE, pdf_copy)

        result = document_path_to_markdown(str(pdf_copy))

        assert isinstance(result, str)
        assert len(result) > 0

    def test_document_path_to_markdown_with_unsupported_extension(self, tmp_path):
        """An unsupported extension (e.g. .txt) should raise a clear error, not silently misconvert."""
        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("plain text content")

        with pytest.raises(Exception):
            document_path_to_markdown(str(txt_file))

    def test_document_path_to_markdown_with_no_extension(self, tmp_path):
        """A path with no extension at all should raise a clear error rather than crash obscurely."""
        no_ext_file = tmp_path / "mystery_file"
        no_ext_file.write_bytes(b"some bytes")

        with pytest.raises(Exception):
            document_path_to_markdown(str(no_ext_file))

    def test_document_path_to_markdown_extension_mismatched_content(self, tmp_path):
        """A file with a supported extension but mismatched actual content should still
        convert correctly, since the underlying markitdown library sniffs the real
        content type rather than trusting the extension blindly."""
        mismatched_file = tmp_path / "fake.pdf"
        shutil.copyfile(self.DOCX_FIXTURE, mismatched_file)

        result = document_path_to_markdown(str(mismatched_file))

        with open(self.DOCX_FIXTURE, "rb") as f:
            expected = binary_document_to_markdown(f.read(), "docx")

        assert result == expected
