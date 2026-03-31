"""Scaffold orchestrator - renders templates and writes output directory."""

import os
import stat
from pathlib import Path

from cairn.prompts import c, info, warn, BOLD, DIM, NC
from cairn.template_engine import create_env, render_template, TEMPLATES_DIR


def _walk_templates(base: Path, prefix: str = "") -> list[str]:
    """Walk a template directory and return relative paths of all .j2 files."""
    results = []
    if not base.is_dir():
        return results
    for item in sorted(base.iterdir()):
        rel = f"{prefix}/{item.name}" if prefix else item.name
        if item.is_dir():
            results.extend(_walk_templates(item, rel))
        elif item.name.endswith(".j2"):
            results.append(rel)
    return results


def _resolve_output_path(template_rel: str, config: dict) -> str:
    """Convert a template relative path to an output file path."""
    out = template_rel
    if out.endswith(".j2"):
        out = out[:-3]
    out = out.replace("__project_slug__", config["project_slug"])
    out = out.replace("__package_name__", config["package_name"])
    return out


def scaffold(config: dict, output_dir: Path) -> None:
    """Scaffold a complete project from templates.

    Template resolution order:
      1. templates/common/              — shared across all project types
      2. templates/{type}/common/       — shared across languages for this type
      3. templates/{type}/{language}/   — type + language specific
    """
    env = create_env()
    project_type = config["project_type"]
    language = config["language"]

    print(f"\n{c(BOLD, 'Generating project...')}")

    template_paths: list[tuple[str, str]] = []  # (template_key, output_rel)

    # 1. Global common templates (LICENSE, .gitignore)
    common_dir = TEMPLATES_DIR / "common"
    for rel in _walk_templates(common_dir):
        template_key = f"common/{rel}"
        output_rel = _resolve_output_path(rel, config)
        template_paths.append((template_key, output_rel))

    # 2. Type-specific common templates (installer, .env, README)
    type_common_dir = TEMPLATES_DIR / project_type / "common"
    for rel in _walk_templates(type_common_dir):
        template_key = f"{project_type}/common/{rel}"
        output_rel = _resolve_output_path(rel, config)
        template_paths.append((template_key, output_rel))

    # 3. Type + language specific templates
    type_lang_dir = TEMPLATES_DIR / project_type / language
    for rel in _walk_templates(type_lang_dir):
        template_key = f"{project_type}/{language}/{rel}"
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

    total = len(template_paths)
    print(f"\n  {c(BOLD, str(total))} files generated in {c(BOLD, str(output_dir))}")
    print()

    slug = config["project_slug"]
    github = config["github_repo_url"]
    print(c(BOLD, "Next steps:"))
    print(f"  1. cd {output_dir}")
    print(f"  2. Review and customize the generated code")
    print(f"  3. git init && git add -A && git commit -m 'Initial scaffold from CAIRN'")
    print(f"  4. Push to {github}")
    if project_type == "doc-search":
        print(f"  5. Users install with:")
        print(f"     {DIM}curl -fsSL https://raw.githubusercontent.com/.../install-{slug} | bash{NC}")
    print()
