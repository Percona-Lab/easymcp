# CAIRN

**Create Any Integration, Run Naturally.** Scaffold production-ready MCP servers for any domain.

Named for the stacked stone trail markers that guide climbers on mountain paths. Part of the [Alpine Toolkit](https://github.com/Percona-Lab).

## What it does

CAIRN generates complete, standalone MCP server projects. You pick a project type, answer a few prompts, and get a working project ready to push to GitHub.

**Three project types:**

| Type | What it builds | Example |
|------|---------------|---------|
| **API integration** | Wrap an external REST API as MCP tools | Slack, Jira, Stripe connectors |
| **Doc search** | Semantic search over GitHub repos with Markdown | percona-dk, internal docs servers |
| **Starter** | Minimal MCP server with one example tool | Quick prototypes, custom tools |

## Install

**As a Claude Code plugin (recommended):**

```
Install this plugin: https://github.com/Percona-Lab/claude-plugins
```

Then ask Claude: "Create a new MCP server" or "Scaffold an API integration for Slack"

**Or download and run directly:**

```bash
curl -fsSL -o /tmp/cairn.whl \
  https://github.com/Percona-Lab/CAIRN/releases/latest/download/cairn_mcp-0.2.0-py3-none-any.whl
uvx --from /tmp/cairn.whl cairn init
```

## What gets generated

### API integration (Python example)

```
slack-mcp/
  .gitignore, LICENSE, .env.example, README.md
  pyproject.toml
  src/slack_mcp/
    connector.py       # API client class with auth + methods
    mcp_server.py      # FastMCP server wrapping connector as tools
```

### Doc search (Python example)

```
acme-dk/
  install-acme-dk          # curl|bash one-liner
  install-acme-dk.ps1      # irm|iex one-liner
  installer.py             # Cross-platform interactive installer
  .gitignore, LICENSE, .env.example, README.md
  pyproject.toml
  src/acme_dk/
    mcp_server.py          # FastMCP with auto-refresh
    ingest.py              # Incremental ingestion pipeline
    server.py              # FastAPI REST API
    source_registry.py     # Source suggestions
```

### Starter

```
my-tool/
  .gitignore, LICENSE, README.md
  pyproject.toml (or package.json)
  src/my_tool/mcp_server.py (or src/mcp-server.js)
```

## Language support

Both Python (FastMCP) and Node.js (@modelcontextprotocol/sdk) templates for all project types.

## License

MIT
