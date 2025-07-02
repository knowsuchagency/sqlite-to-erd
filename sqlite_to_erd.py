import sqlite3
import sys
import click


def get_table_list_query(have_meta):
    """Return the appropriate SQL query for listing tables based on metadata availability."""
    if not have_meta:
        return """
            SELECT tbl_name, NULL AS label, NULL AS color, NULL AS clusterid 
            FROM sqlite_master WHERE type='table'
        """
    
    return """
        SELECT sqlite_master.tbl_name AS tbl_name, 
               meta.cluster.label AS label, 
               meta.cluster.color AS color, 
               meta.cluster.clusterid AS clusterid
        FROM sqlite_master
        LEFT JOIN meta.tbl_cluster ON sqlite_master.tbl_name=meta.tbl_cluster.tbl_name
        LEFT JOIN meta.cluster ON meta.tbl_cluster.clusterid=meta.cluster.clusterid
        LEFT JOIN meta.ignorelist ON sqlite_master.tbl_name=meta.ignorelist.tbl_name
        WHERE meta.ignorelist.tbl_name IS NULL
               AND main.sqlite_master.type='table'
        GROUP BY sqlite_master.tbl_name
        ORDER BY meta.cluster.clusterid
    """


def print_graph_settings(conn, have_meta):
    """Print graph settings from metadata or defaults."""
    if have_meta:
        try:
            cursor = conn.execute("SELECT setting FROM meta.graphsettings")
            for row in cursor:
                print(row[0])
        except sqlite3.Error as e:
            print(f"Warning: Cannot find meta.graphsettings: {e}", file=sys.stderr)
            # Fall back to defaults
            print("rankdir=LR")
            print("splines=true")
            print("overlap=scale")
    else:
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
@click.argument('metadb', type=click.Path(exists=True), required=False)
@click.option('--simple', '-s', is_flag=True, help='Use simple text labels instead of HTML-like table formatting')
def main(dbname, metadb, simple):
    """Generate a GraphViz DOT file from a SQLite database schema.
    
    DBNAME is the path to the SQLite database to visualize.
    METADB is an optional metadata database for clustering and styling.
    """
    try:
        # Open main database
        conn = sqlite3.connect(f"file:{dbname}?mode=ro", uri=True)
        
        # Attach metadata database if provided
        have_meta = False
        if metadb:
            try:
                conn.execute(f'ATTACH DATABASE "{metadb}" AS meta')
                have_meta = True
            except sqlite3.Error as e:
                print(f"Error attaching meta db: {e}", file=sys.stderr)
                sys.exit(1)
        
        # Start DOT graph
        print("digraph sqliteschema {")
        if simple:
            print("node [shape=box];")
        else:
            print("node [shape=plaintext];")
        
        # Print graph settings
        print_graph_settings(conn, have_meta)
        
        # Get table list
        table_query = get_table_list_query(have_meta)
        cursor = conn.execute(table_query)
        tables = cursor.fetchall()
        
        # Track current cluster
        curr_cluster = -1
        
        # Print table nodes with clustering
        for table in tables:
            tbl_name, label, color, cluster_id = table
            
            # Handle cluster transitions
            if cluster_id is None:
                cluster_id = -1
            
            if cluster_id != curr_cluster and curr_cluster != -1:
                print("}")  # Close previous cluster
            
            if cluster_id != curr_cluster and cluster_id != -1:
                print(f"subgraph cluster_{cluster_id} {{")
                if label:
                    print(f'label="{label}"')
                if color:
                    print(f'color="{color}"')
            
            curr_cluster = cluster_id
            
            # Print table node
            print_table_node(conn, tbl_name, simple=simple)
        
        # Close last cluster if needed
        if curr_cluster != -1:
            print("}")
        
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
