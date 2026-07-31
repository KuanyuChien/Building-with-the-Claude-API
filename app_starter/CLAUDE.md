# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Python package implementing document-related tools (format conversion, processing), exposed through an MCP (Model Context Protocol) server so they can be used by AI assistants.

## Commands

```bash
# Create a virtual env and activate it (uv-managed project)
uv venv
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .

# Start the MCP server
uv run main.py

# Run all tests
uv run pytest

# Run a single test file / test
uv run pytest tests/test_document.py
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_pdf
```

## Architecture

- `main.py` is the MCP server entry point. It creates a `FastMCP("docs")` instance and registers each tool function explicitly with `mcp.tool()(function)`, then calls `mcp.run()`. Tools are **not** registered automatically — adding a new tool to a module under `tools/` has no effect until it is also imported and registered in `main.py`.
- `tools/` holds tool implementations as plain Python functions, one concern per module (e.g. `tools/math.py`, `tools/document.py`). These functions are framework-agnostic — they don't import `mcp` or use decorators themselves; `main.py` is the only place that wires a function into the MCP server.
- `tools/document.py` wraps the `markitdown` library to convert binary document data (docx, pdf, etc.) to markdown text.
- `tests/` mirrors `tools/` with one test module per tool module, using pytest. Binary fixtures for document-conversion tests live in `tests/fixtures/`.

## Defining MCP tools

Tools are plain Python functions registered with the MCP server via:

```python
mcp.tool()(my_function)
```

Each tool's docstring is the description the MCP client/AI assistant sees, so it must be written for that audience, not just as internal documentation. Required structure:

- A one-line summary as the first line.
- A more detailed explanation of what the tool does.
- A "When to use" section explaining when (and when not) to use the tool.
- An "Examples" section with concrete input/output examples (doctest-style is used in the existing tools).

All function arguments (and return values) must have appropriate type annotations — don't leave params untyped or typed as `Any` when a more specific type is known.

Parameters must use `Field` from `pydantic` for per-parameter descriptions rather than relying on the docstring alone:

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does")
) -> ReturnType:
    """One-line summary.

    Detailed explanation...

    When to use:
    - ...

    Examples:
    >>> my_tool("x", 1)
    ...
    """
    # Implementation
```

See `tools/math.py`'s `add` function for the canonical example of this pattern.
