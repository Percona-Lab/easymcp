"""Interactive prompt helpers for CAIRN scaffolding."""

import re
import subprocess

# ---------------------------------------------------------------------------
# ANSI colors
# ---------------------------------------------------------------------------
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
BOLD = "\033[1m"
DIM = "\033[2m"
NC = "\033[0m"


def c(color: str, text: str) -> str:
    return f"{color}{text}{NC}"


def info(msg: str) -> None:
    print(f"  {GREEN}{msg}{NC}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}Warning: {msg}{NC}")


def error(msg: str) -> None:
    print(f"  {RED}Error: {msg}{NC}")


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def ask(prompt: str, default: str = "") -> str:
    """Prompt user for text input."""
    display = f" [{default}]" if default else ""
    try:
        value = input(f"  {prompt}{display}: ").strip()
        return value if value else default
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def ask_yn(prompt: str, default: bool = True) -> bool:
    """Prompt user for yes/no answer."""
    hint = "Y/n" if default else "y/N"
    try:
        value = input(f"  {prompt} ({hint}): ").strip().lower()
        if not value:
            return default
        return value in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def ask_choice(prompt: str, options: list[str], default: int = 0) -> int:
    """Prompt user to pick one option. Returns index."""
    for i, opt in enumerate(options):
        marker = f"{BOLD}*{NC} " if i == default else "  "
        print(f"    {marker}{i + 1}) {opt}")
    raw = ask(prompt, default=str(default + 1))
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            return idx
    except ValueError:
        pass
    return default


# ---------------------------------------------------------------------------
# Project type: doc-search prompts
# ---------------------------------------------------------------------------

def ask_data_source() -> dict | None:
    """Prompt user to define one data source (git repo). Returns dict or None to stop."""
    print()
    slug = ask("GitHub repo (owner/repo, or empty to finish)")
    if not slug:
        return None

    if "/" not in slug:
        warn(f"Expected owner/repo format, got '{slug}'. Try again.")
        return ask_data_source()

    name = ask("Display name", default=slug.split("/")[-1].replace("-", " ").title())

    keywords_raw = ask("Keywords for search suggestions (comma-separated)", default="")
    keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()] if keywords_raw else []

    fallback = ask("Approximate number of .md files", default="100")
    try:
        fallback_count = int(fallback)
    except ValueError:
        fallback_count = 100

    return {
        "slug": slug,
        "name": name,
        "keywords": keywords,
        "fallback_doc_count": fallback_count,
    }


def ask_data_source_stacks() -> list[dict]:
    """Prompt user to define stacks of data sources. Returns list of stacks."""
    stacks: list[dict] = []

    print(c(BOLD, "\nDefine your documentation stacks"))
    print(f"  {DIM}A stack is a group of related repos (e.g. 'MySQL stack', 'API docs').{NC}")
    print(f"  {DIM}Users will be able to install/skip each stack during installation.{NC}")

    while True:
        print()
        stack_name = ask("Stack name (or empty to finish)")
        if not stack_name:
            break

        print(f"\n  Add repos to {c(BOLD, stack_name)}:")
        sources: list[dict] = []
        while True:
            source = ask_data_source()
            if source is None:
                break
            sources.append(source)

        if sources:
            stacks.append({"name": stack_name, "sources": sources})
            info(f"Added stack '{stack_name}' with {len(sources)} repo(s)")
        else:
            warn(f"No repos added to '{stack_name}', skipping.")

    return stacks


def _prompts_doc_search(config: dict) -> None:
    """Collect doc-search specific config."""
    stacks = ask_data_source_stacks()

    if not stacks:
        warn("No stacks defined. Adding an example stack you can customize later.")
        stacks = [
            {
                "name": "Documentation",
                "sources": [
                    {
                        "slug": "example/docs",
                        "name": "Example Docs",
                        "keywords": ["docs", "documentation"],
                        "fallback_doc_count": 50,
                    }
                ],
            }
        ]

    print(f"\n{c(BOLD, 'Auto-refresh')}")
    refresh_raw = ask("Default doc update interval in days (0 to disable)", default="7")
    try:
        refresh_days = int(refresh_raw)
    except ValueError:
        refresh_days = 7

    config["stacks"] = stacks
    config["all_sources"] = [s for stack in stacks for s in stack["sources"]]
    config["refresh_days"] = refresh_days


# ---------------------------------------------------------------------------
# Project type: api-integration prompts
# ---------------------------------------------------------------------------

def _ask_tool() -> dict | None:
    """Prompt user to define one MCP tool. Returns dict or None to stop."""
    print()
    name = ask("Tool name (snake_case, or empty to finish)")
    if not name:
        return None

    description = ask("Description", default=f"TODO: describe {name}")
    return {"name": name, "description": description}


def _prompts_api_integration(config: dict) -> None:
    """Collect API integration specific config."""
    print(f"\n{c(BOLD, 'API Service')}")
    service_name = ask("Service name (e.g. Slack, Jira, Stripe)", default="MyService")
    base_url = ask("Base URL", default="https://api.example.com")

    print(f"\n{c(BOLD, 'Authentication')}")
    auth_idx = ask_choice("Auth method", [
        "Bearer token (API key in header)",
        "Basic auth (username + password)",
        "OAuth 2.0 (client credentials)",
        "Custom (you'll implement it)",
    ], default=0)
    auth_methods = ["bearer", "basic", "oauth2", "custom"]
    auth_method = auth_methods[auth_idx]

    print(f"\n{c(BOLD, 'MCP Tools')}")
    print(f"  {DIM}Define the tools your MCP server will expose.{NC}")
    print(f"  {DIM}Each tool wraps an API call. You can add more later.{NC}")
    tools: list[dict] = []
    while True:
        tool = _ask_tool()
        if tool is None:
            break
        tools.append(tool)

    if not tools:
        warn("No tools defined. Adding example tools you can customize later.")
        tools = [
            {"name": "list_items", "description": f"List items from {service_name}"},
            {"name": "get_item", "description": f"Get a single item from {service_name} by ID"},
        ]

    config["service_name"] = service_name
    config["service_slug"] = re.sub(r"[^a-z0-9]+", "_", service_name.lower()).strip("_")
    config["base_url"] = base_url
    config["auth_method"] = auth_method
    config["tools"] = tools


# ---------------------------------------------------------------------------
# Project type: starter prompts
# ---------------------------------------------------------------------------

def _prompts_starter(config: dict) -> None:
    """Starter type needs no extra config."""
    pass


# ---------------------------------------------------------------------------
# Full project prompt flow
# ---------------------------------------------------------------------------

PROJECT_TYPES = [
    ("api-integration", "API integration — wrap an external REST API as MCP tools"),
    ("doc-search", "Doc search — semantic search over GitHub repos with Markdown docs"),
    ("starter", "Starter — minimal MCP server with one example tool"),
]

_TYPE_PROMPTS = {
    "doc-search": _prompts_doc_search,
    "api-integration": _prompts_api_integration,
    "starter": _prompts_starter,
}


def _git_user() -> str:
    """Try to get git user name."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _slugify(name: str) -> str:
    """Convert a project name to a slug (lowercase, hyphens)."""
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", name)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-").lower()
    return slug


def _to_package_name(slug: str) -> str:
    """Convert a slug to a Python package name (underscores)."""
    return slug.replace("-", "_")


def run_prompts() -> dict:
    """Run the full interactive prompt flow. Returns project config dict."""
    print()
    print(c(BOLD, "=" * 60))
    print(c(BOLD, " CAIRN — Create Any Integration, Run Naturally"))
    print(c(BOLD, "=" * 60))
    print()

    # Project type
    print(c(BOLD, "What kind of MCP server?"))
    type_idx = ask_choice("Type", [t[1] for t in PROJECT_TYPES], default=0)
    project_type = PROJECT_TYPES[type_idx][0]
    print()

    # Project basics
    print(c(BOLD, "Project basics"))
    name = ask("Project name", default="my-mcp-server")
    slug = _slugify(name)
    package_name = _to_package_name(slug)
    description = ask("Description", default=f"MCP server for {name}")

    # Language
    print(f"\n{c(BOLD, 'Language')}")
    if project_type == "api-integration":
        lang_options = ["Python (FastMCP)", "Node.js (@modelcontextprotocol/sdk)"]
    elif project_type == "doc-search":
        lang_options = ["Python (FastMCP + ChromaDB)", "Node.js (@modelcontextprotocol/sdk + ChromaDB)"]
    else:
        lang_options = ["Python (FastMCP)", "Node.js (@modelcontextprotocol/sdk)"]
    lang_idx = ask_choice("Language", lang_options, default=0)
    language = "python" if lang_idx == 0 else "nodejs"

    # GitHub
    print(f"\n{c(BOLD, 'Repository')}")
    github_url = ask("GitHub repo URL (where this project will live)", default=f"https://github.com/YOUR_ORG/{slug}")

    # Author
    author = ask("Author", default=_git_user())

    config = {
        "project_type": project_type,
        "project_name": name,
        "project_slug": slug,
        "package_name": package_name,
        "description": description,
        "language": language,
        "github_repo_url": github_url,
        "author": author,
        "license": "MIT",
    }

    # Type-specific prompts
    _TYPE_PROMPTS[project_type](config)

    # Review
    print(f"\n{c(BOLD, 'Review')}")
    print(f"  Type:        {project_type}")
    print(f"  Project:     {name} ({slug})")
    print(f"  Language:    {language}")
    print(f"  Description: {description}")
    print(f"  GitHub:      {github_url}")
    if project_type == "doc-search":
        stacks = config.get("stacks", [])
        print(f"  Stacks:      {len(stacks)} ({sum(len(s['sources']) for s in stacks)} repos)")
        print(f"  Refresh:     every {config.get('refresh_days', 7)} days")
    elif project_type == "api-integration":
        print(f"  Service:     {config.get('service_name')} ({config.get('auth_method')})")
        print(f"  Tools:       {len(config.get('tools', []))}")
    print(f"  Author:      {author}")
    print()

    if not ask_yn("Generate project?", default=True):
        error("Cancelled.")
        raise SystemExit(1)

    return config
