"""Jinja2 template engine with alternate delimiters to avoid {} conflicts."""

import importlib.resources
from pathlib import Path

import jinja2


def _find_templates_dir() -> Path:
    """Find the templates directory, checking both dev and installed locations."""
    # Dev: templates/ next to pyproject.toml
    dev_path = Path(__file__).resolve().parent.parent.parent / "templates"
    if dev_path.is_dir():
        return dev_path

    # Installed: look in package data
    try:
        ref = importlib.resources.files("easymcp") / "templates"
        installed_path = Path(str(ref))
        if installed_path.is_dir():
            return installed_path
    except Exception:
        pass

    raise FileNotFoundError(
        "Cannot find easyMCP templates directory. "
        "Expected at: " + str(dev_path)
    )


TEMPLATES_DIR = _find_templates_dir()


def create_env() -> jinja2.Environment:
    """Create a Jinja2 environment with alternate delimiters.

    Uses <% %> for blocks and << >> for variables to avoid conflicts
    with Python dicts, f-strings, and JavaScript template literals.
    """
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<#",
        comment_end_string="#>",
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(env: jinja2.Environment, template_path: str, context: dict) -> str:
    """Render a single template with the given context."""
    template = env.get_template(template_path)
    return template.render(**context)
