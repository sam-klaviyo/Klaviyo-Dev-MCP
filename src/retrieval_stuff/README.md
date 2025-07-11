# Retrieval Stuff - Developer Guide

This directory contains the core retrieval and indexing infrastructure for the Klaviyo Developer MCP. It's designed to be extensible and easy to add new data sources.

## Architecture Overview

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Source   │ -> │ Document Parser │ -> │ Vector Index    │
│   (Scraper)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        |
                                                        v
                                               ┌─────────────────┐
                                               │   Retriever     │
                                               │                 │
                                               └─────────────────┘
```

### Core Components

1. **Document Parsers** (`document_parser.py`): Convert raw data into chunked Document objects
2. **Vector Indexes** (`index.py`): Create and manage vector embeddings for retrieval
3. **Retrievers** (`retriever.py`): Query the indexes and return relevant documents
4. **Data Scrapers** (optional): Fetch data from external sources (e.g., `confluence_scraper.py`)
5. **Setup Integration** (`../setup_index.py`): Build and configure indexes

## Adding a New Data Source

To add a new data source, you need to implement these components:

### 1. Create a Document Parser

Extend the `DocumentParser` base class in `document_parser.py`:

- **`read_documents()`**: Read raw data from your source
- **`parse_document()`**: Convert raw data to Document objects with metadata
- **`chunk_document()`**: Split documents into chunks (use shared `chunk_document()` function)
- **`get_documents()`**: Main method that orchestrates the process

See `ConfluenceDocumentParser` and `EngHandbookDocumentParser` for examples.

### 2. Create an Index Builder

Add a new builder class to `setup_index.py`:

- Extend `IndexBuilder` base class
- Implement `build()` method
- Add CLI arguments to the main parser
- Add validation and build logic

### 3. Create a Data Scraper (Optional)

If your data source requires fetching from external APIs:

- Create a scraper class (see `confluence_scraper.py`)
- Handle authentication, rate limiting, and error handling
- Save data locally before parsing

### 4. Add MCP Integration

Update the MCP server (`src/mcp_server/main.py`) to:

- Add retriever for your new index
- Add command-line arguments
- Handle queries appropriately

## Best Practices

### Document Processing
- **Consistent Metadata**: Always include `source`, `title`, and other relevant metadata
- **Chunking Strategy**: Use the shared `chunk_document()` function
- **Error Handling**: Gracefully handle parsing errors and continue processing
- **Progress Tracking**: Use `tqdm` for long-running operations

### Index Management
- **Naming Convention**: Use descriptive, consistent index names
- **Default Paths**: Follow the pattern `./index/source_name_index`
- **Configuration**: Make chunk size, embedding model, and dimension configurable

### Integration
- **CLI Arguments**: Follow existing patterns for argument naming
- **Help Text**: Provide clear descriptions and examples
- **Validation**: Validate inputs and provide helpful error messages

## Common Patterns

### File-based Data Sources
- Use `SimpleDirectoryReader` for simple file processing
- Handle various file formats (PDF, HTML, TXT, etc.)
- Preserve file metadata (path, modified date, etc.)

### API-based Data Sources
- Implement rate limiting and retries
- Cache API responses to avoid re-fetching
- Handle pagination for large datasets
- Store API responses as JSON files first, then parse

### Database Sources
- Use connection pooling for performance
- Stream large result sets to avoid memory issues
- Handle connection failures gracefully

## Testing Your Integration

1. **Unit Tests**: Test your document parser with sample data
2. **Integration Test**: Run the full pipeline with a small dataset
3. **Performance Test**: Measure indexing time and memory usage
4. **Retrieval Test**: Verify that relevant documents are retrieved

## Examples

See existing implementations for reference:
- **Confluence**: `confluence_scraper.py` + `ConfluenceDocumentParser`
- **Engineering Handbook**: `EngHandbookDocumentParser` (file-based)

## Support

For questions or help with adding new data sources:
1. Check existing implementations for patterns
2. Review the base classes for required methods
3. Test with small datasets first
4. Consider performance implications for large datasets
