---
name: cairn
description: >
  CAIRN — Create Any Integration, Run Naturally. Scaffold production-ready
  MCP server projects for any domain. Use this skill when the user wants to
  create a new MCP server, scaffold an API integration, build a doc search
  tool, or start a minimal MCP project. Trigger phrases: "create an MCP
  server", "scaffold MCP", "new MCP project", "build an API integration",
  "wrap this API as MCP tools", "like percona-dk but for", "like IBEX but
  for", "cairn", "scaffold". Three project types: api-integration (wrap
  REST APIs as MCP tools), doc-search (semantic search over Markdown repos),
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

### 3. Starter
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
1. **Project type** — API integration, Doc search, or Starter
2. **Project name** and description
3. **Language** — Python (FastMCP) or Node.js (@modelcontextprotocol/sdk)
4. **Type-specific config:**
   - API integration: service name, base URL, auth method, tool definitions
   - Doc search: stacks (groups of repos), keywords, refresh interval
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
4. **Starter:** Add more `@mcp.tool()` functions
5. **Node.js projects:** Run `npm install && npm run build` to bundle `dist/`
6. `git init && git add -A && git commit -m "Initial scaffold from CAIRN"`
7. Push to GitHub

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

## Installing in Claude Desktop

After building, the MCP server must be registered in **both** config
locations to be available everywhere:

### 1. Claude Code CLI (`~/.claude.json`)

```bash
claude mcp add <name> -- node /absolute/path/to/dist/mcp-server.js
```

### 2. Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)

Add an entry to the `mcpServers` object:

```json
{
  "mcpServers": {
    "<name>": {
      "command": "node",
      "args": ["/absolute/path/to/dist/mcp-server.js"]
    }
  }
}
```

The server will appear under **Desktop** in the Connectors panel with a
**LOCAL DEV** badge. Restart Claude Desktop after editing the config.
