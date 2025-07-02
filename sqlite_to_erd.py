import sqlite3
import sys
import subprocess
import click


def get_table_list_query():
    """Return SQL query for listing tables."""
    return "SELECT tbl_name FROM sqlite_master WHERE type='table'"


def print_graph_settings():
    """Print default graph settings."""
    print("rankdir=LR")
    print("splines=true")
    print("overlap=scale")


def print_table_node(conn, table_name, cols=4, simple=False):
    """Print a table node with its columns in DOT format."""
    # Get table info
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    if simple:
        # Simple format: table name with columns listed below
        column_info = [f"{col[1]} ({col[2]})" for col in columns]
        label = f"{table_name}\\n" + "\\n".join(column_info)
        print(f'{table_name} [label="{label}", shape=box];')
    else:
        # HTML-like format with table cells
        # Start table node
        print(f'{table_name} [label=<<TABLE CELLSPACING="0"><TR><TD COLSPAN="{cols}"><U>{table_name}</U></TD></TR>', end='')
        
        # Print columns in rows
        for i, col in enumerate(columns):
            col_name = col[1]  # Column name is at index 1
            col_type = col[2]  # Column type is at index 2
            
            if i % cols == 0:
                print('<TR>', end='')
            
            print(f'<TD PORT="{col_name}">{col_name}<BR/><FONT POINT-SIZE="10">{col_type}</FONT></TD>', end='')
            
            if (i + 1) % cols == 0:
                print('</TR>', end='')
        
        # Close any open row
        if len(columns) % cols != 0:
            print('</TR>', end='')
        
        print('</TABLE>>];')


def print_foreign_keys(conn, table_name, simple=False):
    """Print foreign key relationships for a table."""
    cursor = conn.execute(f"PRAGMA foreign_key_list({table_name})")
    for fk in cursor:
        # fk[2] = referenced table, fk[3] = from column, fk[4] = to column
        if simple:
            # Simple format without ports
            print(f"{table_name} -> {fk[2]};")
        else:
            # HTML format with specific ports
            print(f"{table_name}:{fk[3]} -> {fk[2]}:{fk[4]};")


@click.command()
@click.argument('dbname', type=click.Path(exists=True))
@click.option('--simple', '-s', is_flag=True, help='Use simple text labels instead of HTML-like table formatting')
@click.option('--png', type=click.Path(), help='Generate PNG file directly using GraphViz dot')
def main(dbname, simple, png):
    """Generate a GraphViz DOT file from a SQLite database schema.
    
    DBNAME is the path to the SQLite database to visualize.
    """
    # If PNG output is requested, capture DOT output and pipe through GraphViz
    if png:
        import io
        import contextlib
        
        # Capture stdout
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            generate_dot(dbname, simple)
        
        # Pipe through dot to generate PNG
        try:
            dot_process = subprocess.run(
                ['dot', '-Tpng', '-o', png],
                input=output.getvalue(),
                text=True,
                capture_output=True,
                check=True
            )
            print(f"PNG generated: {png}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error running GraphViz dot: {e}", file=sys.stderr)
            if e.stderr:
                print(e.stderr, file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Error: GraphViz 'dot' command not found. Please install GraphViz.", file=sys.stderr)
            sys.exit(1)
    else:
        generate_dot(dbname, simple)


def generate_dot(dbname, simple):
    """Generate DOT output for the database schema."""
    try:
        # Open main database
        conn = sqlite3.connect(f"file:{dbname}?mode=ro", uri=True)
        
        # No metadata database support
        
        # Start DOT graph
        print("digraph sqliteschema {")
        if simple:
            print("node [shape=box];")
        else:
            print("node [shape=plaintext];")
        
        # Print graph settings
        print_graph_settings()
        
        # Get table list
        table_query = get_table_list_query()
        cursor = conn.execute(table_query)
        tables = cursor.fetchall()
        
        # Print table nodes
        for table in tables:
            tbl_name = table[0]
            # Print table node
            print_table_node(conn, tbl_name, simple=simple)
        
        # Print foreign key relationships
        cursor = conn.execute(table_query)
        for table in cursor:
            tbl_name = table[0]
            print_foreign_keys(conn, tbl_name, simple=simple)
        
        # Close graph
        print("}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
