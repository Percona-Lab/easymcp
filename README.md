# easyMCP

Scaffold production-ready MCP servers for **any domain** — with polished cross-platform installers that guide your users through setup.

You define your data sources. easyMCP generates a complete, standalone project that includes everything your users need to install and run it: interactive prompts, progress bars, time estimates, and auto-configuration of AI clients. One command to scaffold. One command for your users to install.

## What easyMCP does

easyMCP is a project generator. You answer a few questions — project name, language, data sources — and it outputs a complete MCP server project with:

**For you (the builder):**
- A working MCP server, REST API, and ingestion pipeline — ready to customize
- Python (FastMCP + ChromaDB + FastAPI) or Node.js (@modelcontextprotocol/sdk + ChromaDB + Express)
- All the boilerplate: `pyproject.toml` / `package.json`, `.env`, `.gitignore`, `LICENSE`, `README`

**For your users (the installers):**
- `curl | bash` / `irm | iex` one-liner install scripts
- A cross-platform interactive installer (`installer.py`) with:
  - ANSI colors with Windows support
  - Interactive stack selection — "Install all / Skip / Choose individually"
  - Live time and disk estimates per repo (fetched from GitHub API in parallel)
  - Review loop before committing
  - Progress bars during embedding
  - Auto-detection and configuration of Claude Desktop and Claude Code
  - Incremental re-ingestion (only re-embeds files that changed)
  - Smart rerun detection (existing install becomes update flow)

The generated project is **standalone** — no runtime dependency on easyMCP. Push it to GitHub and your users install with a one-liner.

## Install

**As a Claude Code plugin (recommended):**

```
Install this plugin: https://github.com/Percona-Lab/easymcp
```

Then ask Claude: "Create a new MCP server for my docs"

**Or download the plugin zip** from the [latest release](https://github.com/Percona-Lab/easymcp/releases/latest) and extract to `~/.claude/plugins/easymcp/`

**Or run the CLI directly:**

```bash
curl -fsSL -o /tmp/easymcp.whl \
  https://github.com/Percona-Lab/easymcp/releases/latest/download/easymcp-0.1.0-py3-none-any.whl
uvx --from /tmp/easymcp.whl easymcp init
```

Requires [uv](https://docs.astral.sh/uv/). Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## What gets generated

```
acme-docs/
  install-acme-docs          # Bash bootstrap (curl|bash one-liner)
  install-acme-docs.ps1      # PowerShell bootstrap (irm|iex one-liner)
  installer.py               # Cross-platform interactive installer (stdlib only)
  README.md                  # With install instructions, MCP config examples
  LICENSE, .gitignore, .env.example

  # Python template:
  pyproject.toml
  src/acme_docs/
    mcp_server.py             # FastMCP server with auto-refresh
    ingest.py                 # Incremental ingestion (file hashing, ChromaDB)
    server.py                 # FastAPI REST API (/search, /health, /stats)
    source_registry.py        # Keyword-based source suggestions

  # Node.js template:
  package.json
  src/
    mcp-server.js             # @modelcontextprotocol/sdk server
    ingest.js                 # Ingestion pipeline
    server.js                 # Express REST API
    source-registry.js        # Source suggestions
```

## How it works

easyMCP is a Python CLI distributed as a wheel via [GitHub releases](https://github.com/Percona-Lab/easymcp/releases). It's also available as a Claude Code plugin through the [Percona claude-plugins marketplace](https://github.com/Percona-Lab/claude-plugins).

Templates use Jinja2 with alternate delimiters (`<% %>` for blocks, `<< >>` for variables) to avoid conflicts with Python `{}` and JavaScript template literals.

## Project structure

```
easymcp/
  pyproject.toml              # CLI package
  src/easymcp/
    cli.py                    # Click-based CLI
    scaffold.py               # Template rendering + file output
    prompts.py                # Interactive prompt helpers
    template_engine.py        # Jinja2 with alternate delimiters
    validators.py             # Input validation
  templates/
    common/                   # Shared: installer, README, LICENSE, etc.
    python/                   # Python-specific templates
    nodejs/                   # Node.js-specific templates
```

## License

MIT
