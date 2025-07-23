from mcp.server.fastmcp import FastMCP
import llm_schema
import os
from datetime import datetime

mcp = FastMCP("TAPTools")

# -------- tool 1 --------
@mcp.tool()
def list_tables(url: str) -> str:
    """Return (name, description) for every table on a TAP server."""
    tables_data = [ {"name": n, "description": d}
                    for n, d in llm_schema.list_tables_iterable(url) ]
    
    # Create schema_info directory if it doesn't exist
    os.makedirs("schema_info", exist_ok=True)
    
    # Create a filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("schema_info", f"tap_tables_{timestamp}.txt")
    
    # Save to file as formatted text
    with open(filename, 'w', encoding='utf-8') as f:
        for table in tables_data:
            f.write(f"Table: {table['name']}\n")
            f.write(f"Description: {table['description']}\n\n")
    
    return filename

# -------- tool 2 --------
@mcp.tool()
def list_columns(table: str, url: str) -> str:
    """Return column metadata for one table."""
    columns_data = list(llm_schema.list_columns_iterable(table, url))
    
    # Create schema_info directory if it doesn't exist
    os.makedirs("schema_info", exist_ok=True)
    
    # Create a filename with timestamp and sanitized table name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_table_name = table.replace('/', '_').replace('\\', '_').replace(':', '_')
    filename = os.path.join("schema_info", f"tap_columns_{safe_table_name}_{timestamp}.txt")
    
    # Save to file as formatted text
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Columns for table: {table}\n")
        f.write("=" * 50 + "\n\n")
        for column in columns_data:
            f.write(f"{column}\n")
    
    return filename

# -------- tool 3 --------
@mcp.tool()
def generate_schema(url: str) -> str:
    """Return a markdown-formatted TAP schema suitable for LLMs."""
    schema_content = llm_schema.generate_llm_schema(url)
    
    # Create schema_info directory if it doesn't exist
    os.makedirs("schema_info", exist_ok=True)
    
    # Create a filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("schema_info", f"tap_schema_{timestamp}.md")
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(schema_content)
    
    return filename

if __name__ == "__main__":
    mcp.run()      # stdio transport