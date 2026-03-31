"""Input validation helpers for easyMCP scaffolding."""

import re


def validate_project_name(name: str) -> str | None:
    """Validate a project name. Returns error message or None if valid."""
    if not name:
        return "Project name cannot be empty."
    if len(name) > 100:
        return "Project name is too long (max 100 characters)."
    return None


def validate_slug(slug: str) -> str | None:
    """Validate a project slug. Returns error message or None if valid."""
    if not slug:
        return "Slug cannot be empty."
    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", slug) and len(slug) > 1:
        return "Slug must contain only lowercase letters, numbers, and hyphens."
    if slug.startswith("-") or slug.endswith("-"):
        return "Slug cannot start or end with a hyphen."
    return None


def validate_repo_url(url: str) -> str | None:
    """Validate a GitHub repo URL. Returns error message or None if valid."""
    if not url:
        return None  # optional
    pattern = r"^https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$"
    if not re.match(pattern, url):
        return "Expected format: https://github.com/owner/repo"
    return None


def validate_repo_slug(slug: str) -> str | None:
    """Validate an owner/repo slug. Returns error message or None if valid."""
    if not slug:
        return "Repo slug cannot be empty."
    if "/" not in slug:
        return "Expected owner/repo format (e.g. acme/docs)."
    parts = slug.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return "Expected owner/repo format (e.g. acme/docs)."
    return None
