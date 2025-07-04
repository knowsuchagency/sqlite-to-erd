# sqlite-to-erd

Convert SQLite database schemas into Entity Relationship Diagrams (ERDs) using GraphViz.

## Features

- 📊 Visualize SQLite database schemas as ERDs
- 🔗 Automatic foreign key relationship detection
- 📐 Two rendering modes: HTML-like tables or simple boxes
- 🖼️ Direct PNG generation with `--png` flag
- 🔒 Read-only database access for safety

## Installation

### Option 1: Run directly with uvx (recommended)

Requires Python 3.12+ and [uvx](https://github.com/astral-sh/uv).

```bash
# Install GraphViz (required for image generation)
# macOS: brew install graphviz
# Ubuntu: sudo apt-get install graphviz
# Windows: https://graphviz.org/download/

# Run directly from PyPI without installing
uvx sqlite-to-erd database.db
```

### Option 2: Local installation

```bash
# Clone the repository
git clone https://github.com/knowsuchagency/sqlite-to-erd.git
cd sqlite-to-erd

# Install dependencies
uv sync

# Install GraphViz (for image generation)
# macOS: brew install graphviz
# Ubuntu: sudo apt-get install graphviz
# Windows: https://graphviz.org/download/
```

## Usage

### Basic Usage

**With uvx (run directly from PyPI):**

```bash
# Generate DOT format output
uvx sqlite-to-erd database.db

# Generate PNG directly
uvx sqlite-to-erd database.db --png schema.png

# Use simple box format instead of HTML tables
uvx sqlite-to-erd database.db --simple
```

**With local installation:**

```bash
# Generate DOT format output
uv run sqlite_to_erd.py database.db

# Generate PNG directly
uv run sqlite_to_erd.py database.db --png schema.png

# Pipe to GraphViz for other formats
uv run sqlite_to_erd.py database.db | dot -Tsvg -o schema.svg

# Use simple box format instead of HTML tables
uv run sqlite_to_erd.py database.db --simple

# Combine options
uv run sqlite_to_erd.py database.db --simple --png simple_schema.png
```

### Quick Examples

```bash
# Test with included examples
just fk-png      # Creates test_fk.png
just complex-png # Creates complex_test.png
```

## Output Format

The tool generates GraphViz DOT format, which can be:

- Piped to `dot`, `neato`, `fdp`, etc. for different layouts
- Exported to PNG, SVG, PDF, and other formats
- Edited manually for fine-tuning

## Examples

### Simple Database

```bash
echo "
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
" | sqlite3 blog.db

# With uvx
uvx sqlite-to-erd blog.db --png blog.png

# Or with local installation
uv run sqlite_to_erd.py blog.db --png blog.png
```

## Development

```bash
# Run tests
just fk        # Test foreign key visualization
just complex   # Test complex schema

# Generate test images
just fk-png
just complex-png
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Pull requests welcome! Please test your changes with the included test databases.
