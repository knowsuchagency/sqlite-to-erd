# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a SQLite schema visualization tool that generates Entity Relationship Diagrams (ERDs) from SQLite databases using GraphViz DOT format.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the tool
uv run sqlite_to_erd.py <database.db> [metadata.db] [--simple]

# Test with example databases
just fk        # Generate DOT for test_fk.db
just fk-png    # Generate PNG for test_fk.db
just complex   # Generate DOT for complex_test.db
just complex-png # Generate PNG for complex_test.db
```

## Architecture

The entire application is in `sqlite_to_erd.py`:
- `get_table_list_query()` - SQL query generation for table listing
- `print_graph_settings()` - GraphViz configuration output
- `print_table_node()` - Table rendering in DOT format
- `print_foreign_keys()` - Foreign key relationship visualization
- `main()` - Click-based CLI entry point

## Key Features

1. **Metadata Support**: Optional second database for clustering, styling, and filtering tables
2. **Two Rendering Modes**: HTML-like tables with ports or simple box format (`--simple`)
3. **Read-only Operation**: All databases opened in read-only mode for safety
4. **Foreign Key Visualization**: Automatic detection and display of relationships

## Testing

Test databases are provided:
- `test_fk.db` - Simple database with foreign keys
- `complex_test.db` - More complex schema for testing

Use the justfile commands to quickly test changes and verify output.