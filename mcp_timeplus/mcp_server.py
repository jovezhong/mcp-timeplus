import logging
from typing import Sequence

import timeplus_connect
from timeplus_connect.driver.binding import quote_identifier, format_query_value
from dotenv import load_dotenv
from fastmcp import FastMCP

MCP_SERVER_NAME = "mcp-timeplus"
from mcp_timeplus.mcp_env import config

import json, os, time
from confluent_kafka.admin import (AdminClient)
from confluent_kafka import Consumer

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
    "confluent-kafka",
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
def list_tables(database: str = 'default', like: str = None):
    logger.info(f"Listing tables in database '{database}'")
    client = create_timeplus_client()
    query = f"SHOW STREAMS FROM {quote_identifier(database)}"
    if like:
        query += f" LIKE {format_query_value(like)}"
    result = client.command(query)

    # Get all table comments in one query
    table_comments_query = f"SELECT name, comment FROM system.tables WHERE database = {format_query_value(database)}"
    table_comments_result = client.query(table_comments_query)
    table_comments = {row[0]: row[1] for row in table_comments_result.result_rows}

    # Get all column comments in one query
    column_comments_query = f"SELECT table, name, comment FROM system.columns WHERE database = {format_query_value(database)}"
    column_comments_result = client.query(column_comments_query)
    column_comments = {}
    for row in column_comments_result.result_rows:
        table, col_name, comment = row
        if table not in column_comments:
            column_comments[table] = {}
        column_comments[table][col_name] = comment

    def get_table_info(table):
        logger.info(f"Getting schema info for table {database}.{table}")
        schema_query = f"DESCRIBE STREAM {quote_identifier(database)}.{quote_identifier(table)}"
        schema_result = client.query(schema_query)

        columns = []
        column_names = schema_result.column_names
        for row in schema_result.result_rows:
            column_dict = {}
            for i, col_name in enumerate(column_names):
                column_dict[col_name] = row[i]
            # Add comment from our pre-fetched comments
            if table in column_comments and column_dict['name'] in column_comments[table]:
                column_dict['comment'] = column_comments[table][column_dict['name']]
            else:
                column_dict['comment'] = None
            columns.append(column_dict)

        create_table_query = f"SHOW CREATE STREAM {database}.`{table}`"
        create_table_result = client.command(create_table_query)

        return {
            "database": database,
            "name": table,
            "comment": table_comments.get(table),
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
def run_sql(query: str):
    logger.info(f"Executing query: {query}")
    client = create_timeplus_client()
    try:
        readonly = 1 if config.readonly else 0
        res = client.query(query, settings={"readonly": readonly})
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

@mcp.tool()
def list_kafka_topics():
    logger.info("Listing all topics in the Kafka cluster")
    admin_client = AdminClient(json.loads(os.environ['TIMEPLUS_KAFKA_CONFIG']))
    topics = admin_client.list_topics(timeout=10).topics
    topics_array = []
    for topic, detail in topics.items():
        topic_info = {"topic": topic, "partitions": len(detail.partitions)}
        topics_array.append(topic_info)
    return topics_array

@mcp.tool()
def explore_kafka_topic(topic: str, message_count: int = 1):
    logger.info(f"Consuming topic {topic}")
    conf = json.loads(os.environ['TIMEPLUS_KAFKA_CONFIG'])
    conf['group.id'] = f"mcp-{time.time()}"
    client = Consumer(conf)
    client.subscribe([topic])
    messages = []
    for i in range(message_count):
        logger.info(f"Consuming message {i+1}")
        message = client.poll()
        if message is None:
            logger.info("No message received")
            continue
        if message.error():
            logger.error(f"Error consuming message: {message.error()}")
            continue
        else:
            logger.info(f"Received message {i+1}")
            messages.append(json.loads(message.value()))
    client.close()
    return messages

@mcp.tool()
def create_kafka_stream(topic: str):
    logger.info(f"Creating Kafka externalstream for topic {topic}")
    conf = json.loads(os.environ['TIMEPLUS_KAFKA_CONFIG'])
    ext_stream=f"ext_stream_{topic}"
    sql=f"""CREATE EXTERNAL STREAM {ext_stream} (raw string)
    SETTINGS type='kafka',brokers='{conf['bootstrap.servers']}',topic='{topic}',security_protocol='{conf['security.protocol']}',sasl_mechanism='{conf['sasl.mechanism']}',username='{conf['sasl.username']}',password='{conf['sasl.password']}',skip_ssl_cert_check=true
    """
    run_sql(sql)
    logger.info("External Stream created")

    sql=f"CREATE MATERIALIZED VIEW {topic} AS SELECT raw from {ext_stream}"
    run_sql(sql)
    logger.info("MATERIALIZED VIEW created")

    return f"Materialized the Kafka data as {topic}"

def create_timeplus_client():
    client_config = config.get_client_config()
    logger.info(
        f"Creating Timeplus client connection to {client_config['host']}:{client_config['port']} "
        f"as {client_config['username']} "
        f"(secure={client_config['secure']}, verify={client_config['verify']}, "
        f"connect_timeout={client_config['connect_timeout']}s, "
        f"send_receive_timeout={client_config['send_receive_timeout']}s)"
    )

    try:
        client = timeplus_connect.get_client(**client_config)
        # Test the connection
        version = client.server_version
        logger.info(f"Successfully connected to Timeplus server version {version}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Timeplus: {str(e)}")
        raise
