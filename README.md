# Timeplus MCP Server
[![PyPI - Version](https://img.shields.io/pypi/v/mcp-timeplus)](https://pypi.org/project/mcp-timeplus)

An MCP server for Timeplus.

<a href="https://glama.ai/mcp/servers/9aleefsq9s"><img width="380" height="200" src="https://glama.ai/mcp/servers/9aleefsq9s/badge" alt="mcp-timeplus MCP server" /></a>

## Features

### Tools

* `run_select_query`
  - Execute SQL queries on your Timeplus cluster.
  - Input: `sql` (string): The SQL query to execute.
  - All Timeplus queries are run with `readonly = 1` to ensure they are safe.

* `list_databases`
  - List all databases on your Timeplus cluster.

* `list_tables`
  - List all tables in a database.
  - Input: `database` (string): The name of the database.

## Configuration

First, ensure you have the `uv` executable installed. If not, you can install it by following the instructions [here](https://docs.astral.sh/uv/).

1. Open the Claude Desktop configuration file located at:
   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add the following:

```json
{
  "mcpServers": {
    "mcp-timeplus": {
      "command": "uvx",
      "args": ["mcp-timeplus"],
      "env": {
        "TIMEPLUS_HOST": "<timeplus-host>",
        "TIMEPLUS_PORT": "<timeplus-port>",
        "TIMEPLUS_USER": "<timeplus-user>",
        "TIMEPLUS_PASSWORD": "<timeplus-password>",
        "TIMEPLUS_SECURE": "false",
        "TIMEPLUS_VERIFY": "true",
        "TIMEPLUS_CONNECT_TIMEOUT": "30",
        "TIMEPLUS_SEND_RECEIVE_TIMEOUT": "30"
      }
    }
  }
}
```

Update the environment variables to point to your own Timeplus service.

3. Restart Claude Desktop to apply the changes.

You can also try this MCP server with other MCP clients, such as [5ire](https://github.com/nanbingxyz/5ire).

## Development

1. In `test-services` directory run `docker compose up -d` to start a Timeplus Proton server. You can also download it via `curl https://install.timeplus.com/oss | sh`, then start with `./proton server`.

2. Add the following variables to a `.env` file in the root of the repository.

```
TIMEPLUS_HOST=localhost
TIMEPLUS_PORT=8123
TIMEPLUS_USER=default
TIMEPLUS_PASSWORD=
TIMEPLUS_SECURE=false
TIMEPLUS_VERIFY=true
TIMEPLUS_CONNECT_TIMEOUT=30
TIMEPLUS_SEND_RECEIVE_TIMEOUT=30
```

3. Run `uv sync` to install the dependencies. Then do `source .venv/bin/activate`.

4. For easy testing, you can run `fastmcp dev mcp_timeplus/mcp_server.py` to start the MCP server. Click the "Connect" button to connect the UI with the MCP server, then switch to the "Tools" tab to run the available tools: list_databases, list_tables, run_selected_query.

### Environment Variables

The following environment variables are used to configure the Timeplus connection:

#### Required Variables
* `TIMEPLUS_HOST`: The hostname of your Timeplus server
* `TIMEPLUS_USER`: The username for authentication
* `TIMEPLUS_PASSWORD`: The password for authentication

#### Optional Variables
* `TIMEPLUS_PORT`: The port number of your Timeplus server
  - Default: `8443` if HTTPS is enabled, `8123` if disabled
  - Usually doesn't need to be set unless using a non-standard port
* `TIMEPLUS_SECURE`: Enable/disable HTTPS connection
  - Default: `"false"`
  - Set to `"true"` for secure connections
* `TIMEPLUS_VERIFY`: Enable/disable SSL certificate verification
  - Default: `"true"`
  - Set to `"false"` to disable certificate verification (not recommended for production)
* `TIMEPLUS_CONNECT_TIMEOUT`: Connection timeout in seconds
  - Default: `"30"`
  - Increase this value if you experience connection timeouts
* `TIMEPLUS_SEND_RECEIVE_TIMEOUT`: Send/receive timeout in seconds
  - Default: `"300"`
  - Increase this value for long-running queries
* `TIMEPLUS_DATABASE`: Default database to use
  - Default: None (uses server default)
  - Set this to automatically connect to a specific database
