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

## Security Doctrine (MANDATORY — read before generating ANY code)

These rules are non-negotiable. Every MCP server scaffolded by CAIRN MUST follow them.
Violating any rule means the generated project is broken and must be fixed before delivery.

### 1. Credentials NEVER leave the local machine

- **NEVER** put secrets (passwords, API keys, tokens) in MCP config JSON files (`settings.json`, `claude_desktop_config.json`). These files are synced, logged, and displayed in plain text in Claude Desktop's developer settings UI. Secrets placed here are transmitted to Claude/Anthropic servers.
- **NEVER** pass secrets as inline environment variables or command arguments in terminal commands. They appear in terminal output, shell history, process listings, and logs.
- **NEVER** hardcode secrets in generated source files.

### 2. The DOTENV_PATH pattern is the ONLY acceptable credential flow

All credentials MUST be stored in a `.env` file with restricted permissions, and only the path to that file is passed in MCP config:

```json
{
  "command": "/absolute/path/to/uv",
  "args": ["run", "--directory", "/path/to/project", "mcp_server.py"],
  "env": {"DOTENV_PATH": "/path/to/project/.env"}
}
```

The MCP server reads credentials from `.env` at startup. The `.env` file:
- MUST have mode `0o600` (owner read/write only)
- MUST be in `.gitignore`
- MUST NOT be committed to version control

### 3. Password prompts MUST be hidden

Installers that prompt for passwords or secrets MUST use `getpass.getpass()`, never `input()`. The `input()` function echoes characters to the terminal in plain text.

### 4. Commands MUST use absolute paths

Claude Desktop and other MCP hosts run with a restricted PATH that typically does not include `~/.local/bin`, `~/.cargo/bin`, or Homebrew paths. All generated MCP config entries MUST resolve the full absolute path to the command binary (e.g., `/Users/dk/.local/bin/uv`, not `uv`).

Installers MUST include a `resolve_command_path()` function that finds the absolute path via `which`/`shutil.which` with fallback to common install locations.

---

## API-First Doctrine (MANDATORY for API Integration type)

When wrapping a REST API as MCP tools, the API's OpenAPI/Swagger spec is the single source of truth. Guessing endpoints, auth schemes, parameter names, or response shapes causes cascading bugs.

### 1. Always obtain the real spec first

Before writing ANY connector code, do one of:
- Ask the user for the OpenAPI/Swagger spec URL (often at `/spec.yaml`, `/openapi.json`, `/swagger.json`, `/docs`)
- Download it: `curl -fsSL https://api-doc.example.com/spec.yaml -o spec.yaml`
- Ask the user to provide it as a file

If no spec exists, ask the user to provide sample curl commands or Postman collections. Do NOT guess endpoints.

### 2. Generate connector code FROM the spec

Read the spec to extract:
- **Base URL** — from `servers[0].url` (do not guess)
- **Auth scheme** — from `securityDefinitions` / `components.securitySchemes` (header names, locations, flows)
- **Endpoints** — from `paths` (exact paths, methods, parameter names including camelCase)
- **Parameter names** — use exactly as specified (e.g., `filterTimeGt` not `filter_time_gt`, `includePagination` not `include_pagination`)

### 3. Commit the spec to the repo

Save the spec as `spec.yaml` or `openapi.json` in the project root and commit it. This serves as documentation and a reference for future tool additions.

### What went wrong without this:
In the Clari Copilot build, the connector was written by guessing endpoints, auth headers, base URL, and parameter names — all were wrong. The entire client.py and server.py had to be rewritten after downloading the actual spec. This wasted hours and introduced bugs that a spec-first approach would have prevented entirely.

---

## Remote Proxy Doctrine (MANDATORY for servers with remote/SSE mode)

When an MCP server supports both local and remote modes (proxying tool calls to a shared server via SSE), these rules are non-negotiable. They were proven by the vista-data-mcp and relay-bridge (Clari Copilot) deployments.

### 1. Startup must NEVER contact the remote server

The local MCP server must start and register all tools instantly, even off VPN. Connection to the remote is LAZY — only attempted when a tool is actually invoked. This is why we do NOT use `uvx mcp-proxy <remote_url>` — it crashes at startup if DNS can't resolve the remote host, causing Claude Desktop to show "Server disconnected" before the user even tries anything.

### 2. Both modes run the same local server

The MCP config entry must ALWAYS be:
```json
{
  "command": "/absolute/path/to/uv",
  "args": ["run", "--directory", "/path/to/project", "mcp_server.py"],
  "env": { "REMOTE_SSE_URL": "http://host:port/sse" }
}
```
or for local mode:
```json
{
  "command": "/absolute/path/to/uv",
  "args": ["run", "--directory", "/path/to/project", "mcp_server.py"],
  "env": { "DOTENV_PATH": "/path/to/project/.env" }
}
```

NEVER use `uvx mcp-proxy <remote_url>` as the MCP entry. Both modes run the same local Python server — the only difference is the env var that controls the data path.

### 3. Connection errors must return friendly markdown, never crash

Every tool must catch all exceptions from the remote call. DNS failures, timeouts, connection refused — all must return a user-friendly markdown message like:

> **Cannot reach the server.** Connect to Percona VPN and try again.

Never raise, never exit, never let the process die. If the MCP server process exits, Claude Desktop shows "Server disconnected" which confuses users into thinking the installation is broken rather than that they just need VPN.

### 4. The installer clones the repo in BOTH modes

Remote mode is NOT serverless. The installer must `git clone` + `uv sync` (or equivalent) in both remote and local modes, because both modes need the local server code to register tools and act as the proxy. The difference is only:
- **Remote:** env has `REMOTE_SSE_URL`, no `.env` with credentials
- **Local:** env has `DOTENV_PATH`, `.env` contains API credentials

### 5. Tool fallback chain

Every tool function must follow this exact pattern:
```
1. Check if local credentials are configured → call the API directly
2. Else check if REMOTE_SSE_URL is set → forward via _call_remote()
3. Else → return "not configured" message with installer instructions
```

The `_call_remote()` helper opens an SSE connection, forwards the tool name and arguments, extracts text from the response, and returns it. All wrapped in try/except with VPN-friendly error messages.

### What went wrong without this:

In early iterations, `uvx mcp-proxy` was considered but rejected because it connects to the remote at startup and crashes if the host is unreachable. The lazy-connection pattern (connect only on tool invocation) was proven in vista-data-mcp and adopted identically in relay-bridge. Both servers have been running in production on SHERPA since April 2026.

---

## Project Types

### 1. API Integration
Wrap an external REST API as MCP tools. Generates a connector class
(handles auth + HTTP) and an MCP server that exposes connector methods
as tools. Based on the IBEX pattern (Slack, Jira, Notion connectors).

**Requires an OpenAPI/Swagger spec** — see API-First Doctrine above. The spec
determines auth scheme, endpoints, and parameter names. Never guess these.

**Generated files (Python):**
- `connector.py` — API client class with auth headers + request helper
- `mcp_server.py` — FastMCP server wrapping connector methods as tools
- `config.py` — DOTENV_PATH credential loading (see pattern below)
- `spec.yaml` — Downloaded OpenAPI spec (committed as reference)
- `installer.py` — Interactive installer with TTY reopen, cleanup, dual-config, credential validation
- `pyproject.toml`, `.env.example`, `.gitignore`, `README.md`

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
2. **API integration:** The connector is generated from the OpenAPI spec with correct auth, endpoints, and parameter names. Review and test with `curl` before running the MCP server. Add any endpoints not yet wrapped as tools.
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

## Remote Proxy Mode

All Python MCP server templates include built-in remote proxy support via
the `REMOTE_SSE_URL` environment variable. This enables a "shared server"
deployment model where users don't need local credentials.

### How it works

1. Server starts normally — all tools register regardless of config
2. On tool invocation, the fallback chain is:
   - **Local credentials configured?** → execute locally
   - **REMOTE_SSE_URL set?** → forward tool call to remote server via SSE
   - **Neither?** → return friendly "not configured" message with install instructions
3. Remote connection is **lazy** — only attempted when a tool is actually called
4. If the remote server is unreachable (no VPN, etc.), returns a friendly
   error message instead of crashing

### Installer integration

For project types that include an installer (doc-search, data-connector,
api-integration), the installer should offer:

```
Installation mode:
  1) Remote (shared server) — no credentials needed, requires VPN
  2) Local (own credentials) — works offline
```

- **Remote mode:** sets `REMOTE_SSE_URL` in `.env` and the MCP config `env` block
- **Local mode:** sets `DOTENV_PATH` in the MCP config `env` block (credentials in `.env`)
- Both modes clone the repo and install dependencies locally

### Key code pattern (from vista-data-mcp)

```python
_REMOTE_SSE_URL = os.getenv("REMOTE_SSE_URL")

async def _call_remote(tool_name: str, arguments: dict) -> str:
    from mcp.client.sse import sse_client
    from mcp import ClientSession
    try:
        async with sse_client(url=_REMOTE_SSE_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                # extract text blocks from result.content
    except Exception as e:
        # friendly VPN/network error message
```

Each tool follows:
```python
@mcp.tool()
async def my_tool(args) -> str:
    if not _local_configured():
        if _REMOTE_SSE_URL:
            return await _call_remote("my_tool", {"args": args})
        return _NOT_CONFIGURED_MSG
    # ... normal local execution ...
```

Requires `mcp>=1.0` in `pyproject.toml` (provides `mcp.client.sse`).

---

## MCPB Packaging (One-Click Install for Claude Desktop)

CAIRN-scaffolded MCP servers can be packaged as `.mcpb` files — ZIP bundles
that Claude Desktop installs with a single drag-and-drop or click. This
eliminates the need for users to have Python, Node.js, or any dev toolchain.

Spec: https://github.com/modelcontextprotocol/mcpb

### What is a .mcpb file?

A ZIP archive containing:
```
my-server.mcpb
├── manifest.json     ← identity, entry point, config schema, compatibility
├── server/           ← your MCP server code + vendored dependencies
│   ├── mcp_server.py (or index.js)
│   └── ...
└── icon.png          ← optional
```

Claude Desktop reads `manifest.json`, prompts the user for any required
config (API keys via secure input), and launches the server. No terminal,
no git clone, no pip install.

### manifest.json for CAIRN projects

For a Python MCP server (using `uv` runtime — manifest_version 0.3+):

```json
{
  "manifest_version": "0.3",
  "name": "<project-slug>",
  "display_name": "<Project Name>",
  "version": "0.1.0",
  "description": "<description>",
  "author": { "name": "<author>" },
  "license": "MIT",
  "repository": { "url": "https://github.com/<org>/<repo>" },
  "server": {
    "type": "uv",
    "mcp_config": {
      "command": "uv",
      "args": ["run", "--directory", "${__dirname}/server", "mcp_server.py"],
      "env": {
        "DOTENV_PATH": "${__dirname}/server/.env"
      }
    }
  },
  "user_config": {
    "api_key": {
      "type": "string",
      "title": "API Key",
      "description": "Your API key for the service",
      "required": true,
      "sensitive": true
    }
  },
  "tools": [
    { "name": "tool_name", "description": "What this tool does" }
  ],
  "compatibility": {
    "claude_desktop": ">=1.0.0",
    "platforms": ["darwin", "win32", "linux"]
  }
}
```

For Node.js servers, use `"type": "node"` and bundle with esbuild first.

### Key manifest fields

- **`server.type`**: `"uv"` (Python via uv), `"node"`, `"python"`, or `"binary"`
- **`server.mcp_config`**: Same `command`/`args`/`env` as Claude config
- **`${__dirname}`**: Resolves to the bundle's install directory at runtime
- **`user_config`**: Install-time prompts — `sensitive: true` stores in OS keychain
- **`tools`**: Static declarations so Claude Desktop shows them before first launch
- **`compatibility.platforms`**: `["darwin", "win32", "linux"]`

### How to build a .mcpb from a CAIRN project

```bash
# 1. Build/vendor dependencies
# Python:
pip install -t server/vendor -r requirements.txt
# Or for uv-based: just include pyproject.toml, uv resolves at runtime

# Node.js:
npm install && npm run build  # esbuild bundles to dist/

# 2. Create manifest.json (see template above)

# 3. Pack
npx @anthropic-ai/mcpb pack

# 4. Validate
npx @anthropic-ai/mcpb validate

# 5. Optionally sign
npx @anthropic-ai/mcpb sign dist/my-server.mcpb
```

### When to ship .mcpb vs installer

| Audience | Ship |
|----------|------|
| Non-technical users, broad distribution | `.mcpb` — drag-and-drop, no terminal needed |
| Technical users, internal teams | `curl \| bash` installer — more flexible, supports remote proxy mode |
| GitHub releases | Both — `.mcpb` + installer script + wheel |

### Security notes

MCPB has **no sandbox**. The server runs with full user privileges. Follow
the Security Doctrine above — credentials go in `user_config` with
`sensitive: true` (stored in OS keychain), never hardcoded.

### CAIRN integration

When scaffolding a project, CAIRN should generate a `manifest.json` template
alongside the server code. The `npm run pack` or equivalent script can be
added to `package.json` / `Makefile` for easy .mcpb builds.

For Python projects using the `uv` server type, the manifest can reference
`pyproject.toml` directly — `uv` resolves dependencies at runtime, so no
vendoring step is needed.

---

## Installing in Claude

After building, the MCP server must be registered in the AI client config
files. There are two separate configs — update both for full coverage.

**IMPORTANT: Follow the Security Doctrine above.** Never put credentials
in these config files. Only `DOTENV_PATH` goes in `env`.

### 1. Claude Code (`~/.claude/settings.json`)

Add an entry to the `mcpServers` object:

```json
{
  "mcpServers": {
    "<name>": {
      "command": "/absolute/path/to/uv",
      "args": ["run", "--directory", "/absolute/path/to/project", "mcp_server.py"],
      "env": { "DOTENV_PATH": "/absolute/path/to/project/.env" }
    }
  }
}
```

Or use the CLI: `claude mcp add <name> -- /absolute/path/to/uv run --directory /path mcp_server.py`

### 2. Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)

Same `mcpServers` format as above. Use absolute paths for the command — Claude Desktop
has a restricted PATH and cannot find `uv`, `node`, or `python` without full paths.

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

### Credential safety (see Security Doctrine above)
- **NEVER** put credentials in MCP config JSON files — they are displayed in Claude Desktop's developer settings UI and may be synced to Anthropic servers. Use the DOTENV_PATH pattern instead.
- **NEVER** pass passwords, API keys, or secrets as inline environment variables or command arguments in terminal commands. They are displayed in plain text in terminal output, scrollback history, and logs.
- **NEVER** hardcode credentials in generated source files.
- The `.env` file MUST have mode `0o600` and be in `.gitignore`.
- Installers that prompt for passwords MUST use `getpass.getpass()` instead of `input()`.
- MCP server `mcp_server.py` MUST load credentials from `DOTENV_PATH` at startup (see Security Doctrine for the pattern).

### Installer: /dev/tty reopen for piped execution
When an installer is run via `curl -fsSL ... | python3 -`, stdin is the pipe and `input()`/`getpass.getpass()` hit EOF immediately. Every installer MUST include this pattern at the top of `main()`:

```python
def _reopen_tty() -> None:
    """Reopen stdin from /dev/tty when running via curl | python."""
    if not sys.stdin.isatty():
        try:
            sys.stdin = open("/dev/tty", "r")
        except OSError:
            pass  # Windows or no TTY
```

### Installer: Previous-install cleanup
Every installer MUST include a cleanup step that:
1. Scans BOTH `~/.claude/settings.json` AND the platform's `claude_desktop_config.json` for legacy MCP entries (including `DISABLED-` prefixed variants)
2. Detects old install directories from the command path or DOTENV_PATH in those entries
3. Offers to back up `.env` and remove old directories before proceeding
4. Removes stale MCP entries from BOTH config files

### Installer: Dual AI client configuration
The `step_configure_ai_clients()` function MUST write to BOTH:
- `~/.claude/settings.json` (Claude Code) — include `permissions.allow` with `mcp__<name>__*`
- Platform-specific Claude Desktop config:
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%/Claude/claude_desktop_config.json`
  - Linux: `~/.config/claude/claude_desktop_config.json`

Both entries must use identical `command`, `args`, and `env` blocks with absolute paths.

### Installer: Credential validation should be non-blocking
When validating API credentials during install, a failed validation (HTTP 403, timeout, etc.) should WARN and offer to continue, not hard-fail. Paste errors (extra whitespace, truncation) are common. Show troubleshooting tips and let the user proceed.

### DOTENV_PATH loading in server code
The server's config module MUST NOT rely on `pydantic-settings env_file=".env"` alone. MCP hosts launch servers with arbitrary working directories, so relative `.env` paths fail silently. Use this pattern:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

_pkg_dir = Path(__file__).resolve().parent.parent.parent
_dotenv_path = os.getenv("DOTENV_PATH", "")

if _dotenv_path and Path(_dotenv_path).is_file():
    load_dotenv(Path(_dotenv_path))
else:
    for _candidate in [Path.cwd() / ".env", _pkg_dir / ".env"]:
        if _candidate.is_file():
            load_dotenv(_candidate)
            break
    else:
        load_dotenv()
```

This requires `python-dotenv` as an explicit dependency in `pyproject.toml`.

### Remote proxy: never use mcp-proxy
- **WRONG:** `"command": "uvx", "args": ["mcp-proxy", "http://host:port/sse"]` — crashes at startup if DNS fails
- **RIGHT:** Run the local MCP server with `REMOTE_SSE_URL` env var. The server starts instantly, registers tools, and only connects to the remote lazily per tool call.
- Claude Desktop kills MCP servers that fail to start and shows "Server disconnected" — this is indistinguishable from a broken install from the user's perspective.

### Elasticsearch version pinning
- Pin `elasticsearch>=8.0.0,<9.0.0` — v9 has breaking changes in the Python client API.
