---
name: cairn
description: >
  CAIRN — Create Any Integration, Run Naturally. Scaffold production-ready
  MCP server projects for any domain. Use this skill when the user wants to
  create a new MCP server, scaffold an API integration, build a doc search
  tool, or start a minimal MCP project. Trigger phrases: "create an MCP
  server", "scaffold MCP", "new MCP project", "build an API integration",
  "wrap this API as MCP tools", "like percona-dk but for", "like IBEX but
  for", "cairn", "scaffold". Four project types: api-integration (wrap
  REST APIs as MCP tools), doc-search (semantic search over Markdown repos),
  data-connector (read-only database/API access with safety guards),
  and starter (minimal MCP server skeleton).
---

# CAIRN — Create Any Integration, Run Naturally

Scaffold production-ready MCP servers for any domain. Part of the Alpine Toolkit.

Source: https://github.com/Percona-Lab/CAIRN
Release: https://github.com/Percona-Lab/CAIRN/releases/latest

---

## Project Types

### 1. API Integration
Wrap an external REST API as MCP tools. Generates a connector class
(handles auth + HTTP) and an MCP server that exposes connector methods
as tools. Based on the IBEX pattern (Slack, Jira, Notion connectors).

**Generated files (Python):**
- `connector.py` — API client class with auth headers + request helper
- `mcp_server.py` — FastMCP server wrapping connector methods as tools
- `pyproject.toml`, `.env.example`, `README.md`

**Generated files (Node.js):**
- `src/connector.js` — API client with auth + fetch helper
- `src/mcp-server.js` — @modelcontextprotocol/sdk server
- `package.json`, `.env.example`, `README.md`

### 2. Doc Search
Semantic search over GitHub repos containing Markdown documentation.
The percona-dk pattern: clone repos, chunk markdown, embed in ChromaDB,
expose via MCP + REST API. Includes a polished cross-platform installer
with stack selection, progress bars, and AI client auto-detection.

**Generated files (Python):**
- `mcp_server.py` — FastMCP server with auto-refresh
- `ingest.py` — Incremental ingestion with file hashing
- `server.py` — FastAPI REST API
- `source_registry.py` — Source suggestions
- `installer.py` — Cross-platform interactive installer
- Bootstrap scripts, `pyproject.toml`, `.env.example`, `README.md`

### 3. Data Connector
Direct read-only access to databases or APIs (ClickHouse, Elasticsearch,
PostgreSQL, etc.). Generates a connector class per data source with safety
guards (read-only enforcement, row limits, query timeouts) and an MCP
server that exposes query/explore/sample tools. Results formatted as
Markdown tables for LLM consumption. Based on the vista-data-mcp pattern.

**Generated files (Python):**
- `{source}_connector.py` — Per-source client with connection, safety, and Markdown formatting
- `mcp_server.py` — FastMCP server with tools per data source (lazy-loaded, env-gated)
- `installer.py` — Cross-platform installer with credential prompts + AI client auto-config
- `pyproject.toml`, `.env.example`, `README.md`, bootstrap script

**Key patterns:**
- Each data source is optional — tools return "not configured" if env vars are missing
- Connectors are lazy-loaded (imported only when first called) to avoid import errors
- Read-only enforcement: allowlist safe statement prefixes, blocklist mutation keywords
- Results capped at configurable row/hit limits with configurable timeouts
- `uv run --directory` resolves deps from `pyproject.toml` at runtime (no venv needed for MCP entry)

### 4. Starter
Minimal MCP server with one example `hello` tool. User fills in the rest.
Smallest possible starting point for custom MCP servers.

**Generated files (Python):**
- `mcp_server.py` — FastMCP server with one example tool
- `pyproject.toml`, `README.md`

---

## How to Use

### Option 1: Download and run the CLI (recommended)

**Before running the CLI, check if `uv` is installed:**

```bash
which uv || command -v uv
```

If `uv` is not found, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then source the shell profile (or restart the shell) so `uvx` is on PATH.

**Then run the CLI:**

```bash
curl -fsSL -o /tmp/cairn.whl \
  https://github.com/Percona-Lab/CAIRN/releases/latest/download/cairn_mcp-0.2.0-py3-none-any.whl
uvx --from /tmp/cairn.whl cairn init
```

The CLI prompts for:
1. **Project type** — API integration, Doc search, Data connector, or Starter
2. **Project name** and description
3. **Language** — Python (FastMCP) or Node.js (@modelcontextprotocol/sdk)
4. **Type-specific config:**
   - API integration: service name, base URL, auth method, tool definitions
   - Doc search: stacks (groups of repos), keywords, refresh interval
   - Data connector: data sources, connection params, read-only query tools
   - Starter: nothing extra

### Option 2: Guide the user through manual scaffolding

If the CLI isn't available, help the user create the project manually.
Use the CAIRN repo templates as reference for the exact file contents.

---

## After Scaffolding

Tell the user their next steps:

1. `cd <project-dir>` and review the generated code
2. **API integration:** Implement the TODO methods in `connector.py` / `connector.js`
3. **Doc search:** Customize `source_registry.py` keywords and `_build_page_url()` URL pattern
4. **Data connector:** Add query methods to connector classes, tune safety limits
5. **Starter:** Add more `@mcp.tool()` functions
6. **Node.js projects:** Run `npm install && npm run build` to bundle `dist/`
7. `git init && git add -A && git commit -m "Initial scaffold from CAIRN"`
8. Push to GitHub

---

## Node.js Bundling

Node.js projects use esbuild to bundle all dependencies into self-contained
files in `dist/`. This is critical because Claude Desktop and other MCP hosts
launch servers without setting `cwd` to the project directory, so
`node_modules` won't be found at runtime. The bundled `dist/` output has
zero runtime dependencies and should be committed to git.

- `npm run build` — bundles `src/` → `dist/` with all deps inlined
- `npm run dev` — runs source directly (requires `node_modules`)
- `npm run mcp` — runs the bundled server

---

## Installing in Claude

After building, the MCP server must be registered in the AI client config
files. There are two separate configs — update both for full coverage:

### 1. Claude Code (`~/.claude/settings.json`)

Add an entry to the `mcpServers` object:

```json
{
  "mcpServers": {
    "<name>": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/project", "mcp_server.py"],
      "env": { "KEY": "value" }
    }
  }
}
```

Or use the CLI: `claude mcp add <name> -- uv run --directory /path mcp_server.py`

### 2. Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)

Same `mcpServers` format as above.

**IMPORTANT:** `~/.claude.json` is Claude's internal config (themes, tips,
etc.) — do NOT write MCP server entries there. MCP config for Claude Code
goes in `~/.claude/settings.json`.

The server will appear under **Desktop** in the Connectors panel with a
**LOCAL DEV** badge. Restart Claude Desktop after editing the config.

---

## Common Pitfalls (mandatory reading for scaffolding)

These are real bugs discovered in production MCP servers built with CAIRN.
**Every scaffolded project must avoid these:**

### Python dependency installation
- **WRONG:** `uv pip install -e .` — fails without an active venv
- **RIGHT (option A):** `uv venv .venv && uv pip install -e . --python .venv/bin/python` — creates venv explicitly, then installs into it
- **RIGHT (option B):** `uv sync` — creates `.venv` and installs all deps from `pyproject.toml` in one command
- **RIGHT (option C):** Skip install entirely. Use `uv run --directory <path> mcp_server.py` as the MCP entry — this auto-resolves deps from `pyproject.toml` at runtime with no venv needed

### FastMCP constructor
- **WRONG:** `FastMCP("name", description="...")` — `description` was renamed
- **RIGHT:** `FastMCP("name", instructions="...")` — use `instructions=` parameter
- This changed in mcp[cli] >= 1.2.0. Always use `instructions=`.

### Claude config file locations
- `~/.claude/settings.json` — MCP servers for **Claude Code** (has `mcpServers` key)
- `~/Library/Application Support/Claude/claude_desktop_config.json` — MCP servers for **Claude Desktop**
- `~/.claude.json` — Claude's **internal config** (themes, tips, telemetry). **NEVER write MCP entries here.**
- Installers should configure `settings.json` + `claude_desktop_config.json` only.

### Installer safety
- **NEVER** silently overwrite a config file that fails to parse. Ask the user first.
- **ALWAYS** preserve existing keys when adding an `mcpServers` entry (use `config.setdefault("mcpServers", {})`, don't replace the whole file).
- When a config file can't be parsed as JSON, prompt: "Could not parse {path}. Overwrite? (y/N)"

### Credential safety
- **NEVER** pass passwords, API keys, or secrets as inline environment variables or command arguments in terminal commands. They are displayed in plain text in terminal output, scrollback history, and logs.
- **NEVER** hardcode credentials in generated source files. Always use `.env` files or environment variables injected by the MCP host config.
- When testing connections, read credentials from the config file (e.g., `settings.json`, `.env`) via a script — never echo them.
- Installers that prompt for passwords should use `getpass.getpass()` instead of `input()` to avoid displaying the password on screen.

### Elasticsearch version pinning
- Pin `elasticsearch>=8.0.0,<9.0.0` — v9 has breaking changes in the Python client API.
