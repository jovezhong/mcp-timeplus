import logging
from typing import Sequence

import timeplus_connect
from dotenv import load_dotenv
from fastmcp import FastMCP

MCP_SERVER_NAME = "mcp-timeplus"
from mcp_timeplus.mcp_env import config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

load_dotenv()

deps = [
    "timeplus-connect",
    "python-dotenv",
    "uvicorn",
]

mcp = FastMCP(MCP_SERVER_NAME, dependencies=deps)


@mcp.tool()
def list_databases():
    logger.info("Listing all databases")
    client = create_timeplus_client()
    result = client.command("SHOW DATABASES")
    logger.info(f"Found {len(result) if isinstance(result, list) else 1} databases")
    return result


@mcp.tool()
def list_tables(database: str, like: str = None):
    logger.info(f"Listing tables in database '{database}'")
    client = create_timeplus_client()
    query = f"SHOW STREAMS FROM {database}"
    if like:
        query += f" LIKE '{like}'"
    result = client.command(query)

    def get_table_info(table):
        logger.info(f"Getting schema info for table {database}.{table}")
        schema_query = f"DESCRIBE STREAM {database}.`{table}`"
        schema_result = client.query(schema_query)

        columns = []
        column_names = schema_result.column_names
        for row in schema_result.result_rows:
            column_dict = {}
            for i, col_name in enumerate(column_names):
                column_dict[col_name] = row[i]
            columns.append(column_dict)

        create_table_query = f"SHOW CREATE STREAM {database}.`{table}`"
        create_table_result = client.command(create_table_query)

        return {
            "database": database,
            "name": table,
            "columns": columns,
            "create_table_query": create_table_result,
        }

    tables = []
    if isinstance(result, str):
        # Single table result
        for table in (t.strip() for t in result.split()):
            if table:
                tables.append(get_table_info(table))
    elif isinstance(result, Sequence):
        # Multiple table results
        for table in result:
            tables.append(get_table_info(table))

    logger.info(f"Found {len(tables)} tables")
    return tables


@mcp.tool()
def run_select_query(query: str):
    logger.info(f"Executing SELECT query: {query}")
    client = create_timeplus_client()
    try:
        res = client.query(query, settings={"readonly": 1})
        column_names = res.column_names
        rows = []
        for row in res.result_rows:
            row_dict = {}
            for i, col_name in enumerate(column_names):
                row_dict[col_name] = row[i]
            rows.append(row_dict)
        logger.info(f"Query returned {len(rows)} rows")
        return rows
    except Exception as err:
        logger.error(f"Error executing query: {err}")
        return f"error running query: {err}"


def create_timeplus_client():
    client_config = config.get_client_config()
    logger.info(
        f"Creating Timeplus client connection to {client_config['host']}:{client_config['port']} "
        f"as {client_config['username']} "
        f"(secure={client_config['secure']}, verify={client_config['verify']}, "
        f"connect_timeout={client_config['connect_timeout']}s, "
        f"send_receive_timeout={client_config['send_receive_timeout']}s)"

    try:
        client = timeplus_connect.get_client(**client_config)
        # Test the connection
        version = client.server_version
        logger.info(f"Successfully connected to Timeplus server version {version}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Timeplus: {str(e)}")
        raise
