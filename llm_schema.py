import pyvo
import logging
from typing import Tuple, Iterable
import os
# TOKEN = os.environ["ASTRO_DATABASE_TOKEN"] if "ASTRO_DATABASE_TOKEN" in os.environ else None
TOKEN = None
# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def list_tables_iterable(url: str) -> Iterable[Tuple[str, str]]:
    """Lists the names and descriptions of all available tables at the given TAP server URL.

    Args:
        url: The URL of the TAP server.

    Returns:
        An iterable of tuples, where each tuple contains (table_name, table_description).
    """
    if not url or not isinstance(url, str):
        logging.error("Invalid URL provided for list_tables_iterable.")
        raise ValueError("url must be a non-empty string")
        
    try:
        logging.info(f"Attempting to load tables from TAP server: {url}")
        if TOKEN:
            #Replace https:// with https://x-oauth-basic:TOKEN@
            url = url.replace("https://", f"https://x-oauth-basic:{TOKEN}@")
        tap_service = pyvo.dal.TAPService(url)
        tables = tap_service.tables
          
        table_info = []
        for table_name, table_obj in tables.items():
            qualified_name = table_obj.name
            description = table_obj.description if table_obj.description else "No description available"
            table_info.append((qualified_name, description))
        
        logging.info(f"Successfully loaded {len(table_info)} tables with metadata from {url}.")
        return table_info
    except Exception as e:
        logging.error(f"Error loading tables from {url}: {e}", exc_info=True)
        raise RuntimeError(f"Failed to retrieve tables from {url}: {e}")

def list_columns_iterable(table: str, url: str) -> Iterable[str]:
    """Lists the column metadata for a specific table at the given TAP server URL.

    Args:
        table: The fully qualified name of the table.
        url: The URL of the TAP server.

    Returns:
        An iterable of strings, where each string contains the metadata 
        (name, description, unit, datatype) for a column.
    """
    if not table or not isinstance(table, str):
        logging.error(f"Invalid table name provided: {table}")
        raise ValueError("table must be a non-empty string")
    if not url or not isinstance(url, str):
        logging.error(f"Invalid URL provided for list_columns_iterable: {url}")
        raise ValueError("url must be a non-empty string")
        
    try:
        logging.info(f"Attempting to load column metadata for table: {table} at {url}")
        if TOKEN:
            url = url.replace("https://", f"https://x-oauth-basic:{TOKEN}@")
        tap_service = pyvo.dal.TAPService(url)
        
        table_metadata = None
        if table in tap_service.tables:
            table_metadata = tap_service.tables[table]
        else:
            logging.warning(f"Table '{table}' not found directly in tap_service.tables at {url}.")

        if table_metadata:
            column_details = []
            for col in table_metadata.columns:
                description_text = 'No description available'
                if col.description:
                    description_text = ' '.join(str(col.description).replace('\n', ' ').split())
                
                detail_str = (
                    f"`{col.name}` | "
                    f"{description_text} | "
                    f"{col.unit + ' | ' if col.unit else ''}"
                    f"{col.datatype.content if col.datatype else ''}"
                )
                column_details.append(detail_str)
            
            logging.info(f"Found {len(column_details)} columns for table {table} at {url}.")
            return column_details
        else:
            logging.warning(f"Could not load metadata for table: {table} at {url}. Table not found in service's table list.")
            raise ValueError(f"Table '{table}' not found or metadata could not be loaded from {url}")

    except KeyError:
        logging.error(f"Table '{table}' not found in the service at {url} (KeyError).", exc_info=True)
        raise ValueError(f"Table '{table}' not found at {url}. This might indicate an issue with the table name or the service response.")
    except Exception as e:
        logging.error(f"Error loading columns for table {table} at {url}: {e}", exc_info=True)
        raise RuntimeError(f"Failed to retrieve columns for table {table} at {url}: {e}")

def generate_llm_schema(url: str) -> str:
    """
    Generates a formatted schema string for all tables in a TAP service,
    suitable for use with an LLM.

    Args:
        url: The URL of the TAP server.

    Returns:
        A string containing the formatted schema.
    """
    if not url or not isinstance(url, str):
        logging.error("Invalid URL provided for generate_llm_schema.")
        raise ValueError("url must be a non-empty string")

    schema_parts = [f"access_url: {url}\n"]

    try:
        tables = list_tables_iterable(url)
        for table_name, table_description in tables:
            cleaned_table_description = ' '.join(str(table_description).replace('\n', ' ').split()) if table_description else 'No description available'
            
            schema_parts.append(f"\n# `{table_name}`")
            schema_parts.append(f"## Description: {cleaned_table_description}")
            schema_parts.append(f"## Columns:")
            
            try:
                columns = list_columns_iterable(table_name, url)
                columns_line = "\n".join(columns)
                schema_parts.append(columns_line)
            except Exception as e:
                logging.warning(f"Could not retrieve columns for table {table_name} at {url}: {e}")
                schema_parts.append(f"Error retrieving columns for {table_name}: {str(e)}")
            schema_parts.append("")

    except Exception as e:
        logging.error(f"Failed to generate schema for {url}: {e}", exc_info=True)
        schema_parts.append(f"\nError generating schema: Failed to retrieve initial table list from {url}: {str(e)}")
        return "\n".join(schema_parts)

    return "\n".join(schema_parts)

# if __name__ == '__main__':
#     # tap_url_example = "https://cda.cfa.harvard.edu/cxctap/"
    
#     # print(f"Generating LLM schema for: {tap_url_example}")
#     # llm_schema = generate_llm_schema(tap_url_example)
#     # print("\n--- LLM Schema Output ---")
#     # print(llm_schema)
#     # print("--- End of LLM Schema Output ---")

#     # output_filename = "cxc_llm_schema.txt"
#     # try:
#     #     with open(output_filename, "w", encoding="utf-8") as f:
#     #         f.write(llm_schema)
#     #     print(f"\nSchema successfully saved to {output_filename}")
#     # except IOError as e:
#     #     print(f"\nError writing schema to file {output_filename}: {e}")

#     gaia_tap_url = "https://gea.esac.esa.int/tap-server/tap"
#     print(f"\nGenerating LLM schema for: {gaia_tap_url}")
#     llm_schema_gaia = generate_llm_schema(gaia_tap_url)
#     print("\n--- LLM Schema Output (Gaia) ---")
#     print(llm_schema_gaia)
#     print("--- End of LLM Schema Output (Gaia) ---")
#     output_filename_gaia = "gaia_llm_schema.txt"
#     try:
#         with open(output_filename_gaia, "w", encoding="utf-8") as f:
#             f.write(llm_schema_gaia)
#         print(f"\nGaia schema successfully saved to {output_filename_gaia}")
#     except IOError as e:
#         print(f"\nError writing Gaia schema to file {output_filename_gaia}: {e}")