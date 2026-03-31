"""Scaffold orchestrator - renders templates and writes output directory."""

import os
import stat
from pathlib import Path

from easymcp.prompts import c, info, warn, BOLD, DIM, NC
from easymcp.template_engine import create_env, render_template, TEMPLATES_DIR


def _walk_templates(base: Path, prefix: str = "") -> list[str]:
    """Walk a template directory and return relative paths of all .j2 files."""
    results = []
    for item in sorted(base.iterdir()):
        rel = f"{prefix}/{item.name}" if prefix else item.name
        if item.is_dir():
            results.extend(_walk_templates(item, rel))
        elif item.name.endswith(".j2"):
            results.append(rel)
    return results


def _resolve_output_path(template_rel: str, config: dict) -> str:
    """Convert a template relative path to an output file path.

    Handles:
      - Removing .j2 suffix
      - Replacing __project_slug__ with actual slug
      - Replacing __package_name__ with actual package name
    """
    out = template_rel
    # Strip .j2 extension
    if out.endswith(".j2"):
        out = out[:-3]
    # Replace dynamic path segments
    out = out.replace("__project_slug__", config["project_slug"])
    out = out.replace("__package_name__", config["package_name"])
    return out


def scaffold(config: dict, output_dir: Path) -> None:
    """Scaffold a complete project from templates."""
    env = create_env()
    language = config["language"]

    print(f"\n{c(BOLD, 'Generating project...')}")

    # Collect templates: common + language-specific
    template_paths: list[tuple[str, str]] = []  # (template_rel_from_root, output_rel)

    # Common templates
    common_dir = TEMPLATES_DIR / "common"
    if common_dir.is_dir():
        for rel in _walk_templates(common_dir):
            template_key = f"common/{rel}"
            output_rel = _resolve_output_path(rel, config)
            template_paths.append((template_key, output_rel))

    # Language-specific templates
    lang_dir = TEMPLATES_DIR / language
    if lang_dir.is_dir():
        for rel in _walk_templates(lang_dir):
            template_key = f"{language}/{rel}"
            output_rel = _resolve_output_path(rel, config)
            template_paths.append((template_key, output_rel))

    # Render and write each template
    for template_key, output_rel in template_paths:
        output_path = output_dir / output_rel
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = render_template(env, template_key, config)
        output_path.write_text(content)

        # Make bash installer executable
        if output_rel.startswith("install-") and not output_rel.endswith(".ps1"):
            output_path.chmod(output_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        print(f"  {DIM}{output_rel}{NC}")

    # Summary
    total = len(template_paths)
    print(f"\n  {c(BOLD, str(total))} files generated in {c(BOLD, str(output_dir))}")
    print()

    # Next steps
    slug = config["project_slug"]
    github = config["github_repo_url"]
    print(c(BOLD, "Next steps:"))
    print(f"  1. cd {output_dir}")
    print(f"  2. Review and customize the generated code")
    print(f"  3. git init && git add -A && git commit -m 'Initial scaffold from easyMCP'")
    print(f"  4. Push to {github}")
    print(f"  5. Users install with:")
    print(f"     {DIM}curl -fsSL https://raw.githubusercontent.com/.../install-{slug} | bash{NC}")
    print()
