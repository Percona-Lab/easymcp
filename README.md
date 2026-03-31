# easyMCP

Scaffold production-ready MCP servers with polished cross-platform installers. Like `create-react-app` but for MCP servers.

Every generated project gets:
- One-liner install (`curl | bash` / `irm | iex`)
- Interactive stack selection with time/disk estimates
- Incremental ingestion with progress bars
- Auto-detection and configuration of AI clients
- Background auto-refresh in the MCP server

## Quick start

```bash
# Python users
uvx easymcp init

# Node.js users
npx easymcp init
```

The interactive prompts walk you through creating a new MCP project:

1. **Project name** and description
2. **Language** — Python (FastMCP + ChromaDB) or Node.js (@modelcontextprotocol/sdk)
3. **GitHub repo URL** — where the generated project will live
4. **Data sources** — define stacks of git repos with docs
5. **Auto-refresh interval** — how often to check for updates

Then scaffolds a complete project directory, ready to push to GitHub.

## What gets generated

```
acme-docs/
  install-acme-docs          # Bash bootstrap (curl|bash one-liner)
  install-acme-docs.ps1      # PowerShell bootstrap (irm|iex one-liner)
  installer.py               # Cross-platform interactive installer (stdlib only)
  README.md                  # With install instructions, MCP config examples
  LICENSE
  .gitignore
  .env.example

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

## Installer UX

Every generated installer includes:

- **ANSI colors** with Windows ctypes support
- **Interactive prompts** with defaults and EOF handling
- **Parallel GitHub API fetching** with rate limit detection and hardcoded fallbacks
- **Stack selection UI** — "Install all / Skip / Choose individually" with time/disk estimates
- **Review loop** — total estimate, "Modify selection?"
- **Progress bar** during embedding
- **Incremental re-ingestion** via SHA256 file hashes
- **Smart rerun detection** — existing install becomes update flow
- **AI client auto-detection** — Claude Desktop, Claude Code
- **Cross-platform** — macOS, Linux, Windows

## How it works

easyMCP itself is a Python CLI distributed via PyPI. Node.js users get a thin npm wrapper that auto-installs `uv` and delegates to the Python CLI.

Generated projects are **standalone** — no runtime dependency on easyMCP. The scaffolded code is self-contained and hackable.

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
  npm-wrapper/                # Thin npx bridge
    package.json
    bin/easymcp.js
```

## Publishing

Tag a release to publish to both PyPI and npm:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This triggers GitHub Actions workflows that publish:
- **PyPI**: `easymcp` package (enables `uvx easymcp init`)
- **npm**: `easymcp` package (enables `npx easymcp init`)

## License

MIT
