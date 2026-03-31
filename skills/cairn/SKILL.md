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

```bash
curl -fsSL -o /tmp/cairn.whl \
  https://github.com/Percona-Lab/CAIRN/releases/latest/download/cairn_mcp-0.2.0-py3-none-any.whl
uvx --from /tmp/cairn.whl cairn init
```

If `uv` is not installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`

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
5. `git init && git add -A && git commit -m "Initial scaffold from CAIRN"`
6. Push to GitHub
