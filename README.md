# sqlite-to-erd

Convert SQLite database schemas into Entity Relationship Diagrams (ERDs) using GraphViz.

## Features

- =Ê Visualize SQLite database schemas as ERDs
- = Automatic foreign key relationship detection
- <¨ Metadata-driven clustering and styling
- =Ð Two rendering modes: HTML-like tables or simple boxes
- = Read-only database access for safety

## Installation

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
# Clone the repository
git clone https://github.com/yourusername/sqlite-to-erd.git
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

```bash
# Generate DOT format output
uv run sqlite_to_erd.py database.db

# Pipe to GraphViz to create an image
uv run sqlite_to_erd.py database.db | dot -Tpng -o schema.png

# Use simple box format instead of HTML tables
uv run sqlite_to_erd.py database.db --simple
```

### With Metadata Database

Create a metadata database to control clustering, colors, and filtering:

```bash
uv run sqlite_to_erd.py database.db metadata.db
```

The metadata database should contain:
- `clusters` table: Group related tables together
- `cluster_labels` table: Set cluster titles and colors
- `tables_to_ignore` table: Exclude specific tables
- `graph_settings` table: Customize GraphViz settings

### Quick Examples

```bash
# Test with included examples
just fk-png      # Creates test_fk.png
just complex-png # Creates complex_test.png
```

## Metadata Database Schema

To customize your ERD, create a metadata database with these tables:

```sql
-- Group tables into clusters
CREATE TABLE clusters (
    table_name TEXT,
    cluster_name TEXT
);

-- Style clusters
CREATE TABLE cluster_labels (
    cluster_name TEXT PRIMARY KEY,
    cluster_label TEXT,
    cluster_color TEXT
);

-- Ignore specific tables
CREATE TABLE tables_to_ignore (
    table_name TEXT PRIMARY KEY
);

-- Custom GraphViz settings
CREATE TABLE graph_settings (
    setting TEXT,
    value TEXT
);
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

uv run sqlite_to_erd.py blog.db | dot -Tpng -o blog.png
```

### With Clustering
```bash
# Create metadata for clustering
echo "
CREATE TABLE clusters (table_name TEXT, cluster_name TEXT);
INSERT INTO clusters VALUES 
    ('users', 'auth'),
    ('sessions', 'auth'),
    ('posts', 'content'),
    ('comments', 'content');

CREATE TABLE cluster_labels (
    cluster_name TEXT PRIMARY KEY,
    cluster_label TEXT,
    cluster_color TEXT
);
INSERT INTO cluster_labels VALUES 
    ('auth', 'Authentication', 'lightblue'),
    ('content', 'Content Management', 'lightgreen');
" | sqlite3 metadata.db

uv run sqlite_to_erd.py blog.db metadata.db | dot -Tpng -o blog_clustered.png
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

[Add your license here]

## Contributing

Pull requests welcome! Please test your changes with the included test databases.