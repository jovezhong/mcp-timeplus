# Timeplus MCP Server
[![PyPI - Version](https://img.shields.io/pypi/v/mcp-timeplus)](https://pypi.org/project/mcp-timeplus)

An MCP server for Timeplus.

<a href="https://glama.ai/mcp/servers/yvjy4csvo1"><img width="380" height="200" src="https://glama.ai/mcp/servers/yvjy4csvo1/badge" alt="mcp-timeplus MCP server" /></a>

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

This Python package is not published to PyPI yet. Please clone this repo and run `uv sync` to install the dependencies.

1. Open the Claude Desktop configuration file located at:
   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add the following:

```json
{
  "mcpServers": {
    "mcp-timeplus": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--project",
        "/path/to/repo/mcp-timeplus",
        "--python",
        "3.13",
        "mcp-timeplus"
      ],
      "env": {
        "TIMEPLUS_HOST": "<timeplus-host>",
        "TIMEPLUS_PORT": "<timeplus-port>",
        "TIMEPLUS_USER": "<timeplus-user>",
        "TIMEPLUS_PASSWORD": "<timeplus-password>"
      }
    }
  }
}
```

Update the environment variables to point to your own Timeplus service.

3. Locate the command entry for `uv` and replace it with the absolute path to the `uv` executable. This ensures that the correct version of `uv` is used when starting the server. Also point to the absolute path to the `mcp-timeplus` directory. A sample configuration:

```json
{
  "mcpServers": {
    "mcp-timeplus": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "run",
        "--project",
        "/Users/jove/Dev/mcp-timeplus",
        "--python",
        "3.13",
        "mcp-timeplus"
      ],
      "env": {
        "TIMEPLUS_HOST": "localhost",
        "TIMEPLUS_PORT": "8123",
        "TIMEPLUS_USER": "default",
        "TIMEPLUS_PASSWORD": ""
      }
    }
  }
}
```

4. Restart Claude Desktop to apply the changes.

## Development

1. In `test-services` directory run `docker compose up -d` to start a Timeplus Proton server. You can also download it via `curl https://install.timeplus.com/oss | sh`, then start with `./proton server`.

2. Add the following variables to a `.env` file in the root of the repository.

```
TIMEPLUS_HOST=localhost
TIMEPLUS_PORT=8123
TIMEPLUS_USER=default
TIMEPLUS_PASSWORD=
```

3. Run `uv sync` to install the dependencies. Then do `source .venv/bin/activate`.

4. For easy testing, you can run `fastmcp dev mcp_timeplus/mcp_server.py` to start the MCP server. Click the "Connect" button to connect the UI with the MCP server, then switch to the "Tools" tab to run the available tools: list_databases, list_tables, run_selected_query.
