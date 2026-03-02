#!/usr/bin/env python3
"""
stgen-cli — Generate static HTML from YAML config and .stg templates.
"""

import argparse
import os
import sys

import yaml
from bs4 import BeautifulSoup


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {head_content}
    <title>{title}</title>
</head>
<body>
{body_content}
</body>
</html>
"""

LAYOUT_TEMPLATE = "{header}\n{main}\n{footer}"

DEFAULT_GEN_DIR = ".gen"
DEFAULT_INCLUDES_DIR = "includes"
DEFAULT_COMPILED_DIR = "compiled"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def beautify_html(html_data: str) -> str:
    """Return prettified HTML."""
    return BeautifulSoup(html_data, "html.parser").prettify()


def read_yaml(path: str) -> dict:
    """Load and return YAML from a file. Exits on error."""
    path = os.path.normpath(path)
    if not os.path.isfile(path):
        print(f"Error: Config file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def read_html_file(path: str) -> str:
    """Read HTML/fragment file. Exits on error."""
    path = os.path.normpath(path)
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_html_file(path: str, data: str, prettify: bool = True) -> None:
    """Write HTML to file; create parent dirs if needed."""
    path = os.path.normpath(path)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    content = beautify_html(data) if prettify else data
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_includes(base_dir: str, include_list: list) -> str:
    """Concatenate content of included HTML files."""
    parts = []
    for name in include_list or []:
        filepath = os.path.join(base_dir, name)
        parts.append(read_html_file(filepath))
    return "\n".join(parts)


def build_deps(deps: dict) -> str:
    """Build styles, scripts, and extra HTML from dependencies config."""
    styles = deps.get("styles") or []
    scripts = deps.get("scripts") or []
    extra_html = deps.get("html") or ""

    lines = []
    for href in styles:
        lines.append(f'<link rel="stylesheet" href="{href}">')
    for src in scripts:
        lines.append(f'<script src="{src}" defer></script>')
    if extra_html:
        lines.append(extra_html)
    return "\n".join(lines)


def get_stg_pages(template_dir: str) -> list[str]:
    """Return list of page names (no extension) for all .stg files in template_dir."""
    template_dir = os.path.normpath(template_dir)
    if not os.path.isdir(template_dir):
        print(f"Error: Template directory not found: {template_dir}", file=sys.stderr)
        sys.exit(1)
    pages = []
    for name in os.listdir(template_dir):
        if name.endswith(".stg"):
            pages.append(name[:-4])
    return sorted(pages)


# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------

def get_main_content(template_dir: str, page_name: str) -> str:
    """Read .stg template and wrap in <main>."""
    path = os.path.join(template_dir, f"{page_name}.stg")
    content = read_html_file(path)
    return f"<main>\n{content}\n</main>"


def build_page(
    page_name: str,
    config: dict,
    layout: dict,
    gen_dir: str,
    includes_dir: str,
    compiled_dir: str,
) -> str:
    """Build one HTML page. Returns path to written file."""
    template_dir = config.get("template_dir")
    if not template_dir:
        print("Error: page.yml must define 'template_dir'.", file=sys.stderr)
        sys.exit(1)

    base = os.path.dirname(gen_dir)
    template_dir_abs = os.path.normpath(os.path.join(base, template_dir))
    includes_dir_abs = os.path.normpath(os.path.join(base, includes_dir))
    compiled_dir_abs = os.path.normpath(os.path.join(base, compiled_dir))

    layout_sections = layout.get("layout") or layout
    header_includes = (layout_sections.get("header") or {}).get("include") or []
    footer_includes = (layout_sections.get("footer") or {}).get("include") or []

    header = build_includes(includes_dir_abs, header_includes)
    main_content = get_main_content(template_dir_abs, page_name)
    footer = build_includes(includes_dir_abs, footer_includes)

    body = LAYOUT_TEMPLATE.format(header=header, main=main_content, footer=footer)
    head_content = build_deps(config.get("dependencies") or {})
    title = config.get("title") or "Page"

    html = HTML_TEMPLATE.format(
        head_content=head_content,
        title=title,
        body_content=body,
    )

    out_path = os.path.join(compiled_dir_abs, f"{page_name}.html")
    write_html_file(out_path, html)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate static HTML from .stg templates and YAML config.",
        epilog="Examples:\n  %(prog)s                    # Build all pages\n  %(prog)s index about       # Build only index and about",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "pages",
        nargs="*",
        help="Page names to build (e.g. index about). If omitted, build all .stg pages.",
    )
    parser.add_argument(
        "-g", "--gen-dir",
        default=DEFAULT_GEN_DIR,
        help=f"Config directory (default: {DEFAULT_GEN_DIR})",
    )
    parser.add_argument(
        "-i", "--includes",
        default=DEFAULT_INCLUDES_DIR,
        help=f"Includes directory for header/footer (default: {DEFAULT_INCLUDES_DIR})",
    )
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_COMPILED_DIR,
        help=f"Output directory for HTML (default: {DEFAULT_COMPILED_DIR})",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Only print errors",
    )
    args = parser.parse_args()

    base = os.getcwd()
    gen_dir = os.path.normpath(os.path.join(base, args.gen_dir))
    page_yml = os.path.join(gen_dir, "page.yml")
    layout_yml = os.path.join(gen_dir, "layout.yml")

    config = read_yaml(page_yml)
    layout_data = read_yaml(layout_yml)

    template_dir = config.get("template_dir")
    if not template_dir:
        print("Error: page.yml must define 'template_dir'.", file=sys.stderr)
        sys.exit(1)
    template_dir_abs = os.path.normpath(os.path.join(base, template_dir))

    if args.pages:
        pages = args.pages
        for p in pages:
            stg_path = os.path.join(template_dir_abs, f"{p}.stg")
            if not os.path.isfile(stg_path):
                print(f"Error: Template not found: {stg_path}", file=sys.stderr)
                sys.exit(1)
    else:
        pages = get_stg_pages(template_dir_abs)
        if not pages:
            print("No .stg files found in", template_dir_abs, file=sys.stderr)
            sys.exit(1)

    for page_name in pages:
        out_path = build_page(
            page_name,
            config,
            layout_data,
            gen_dir,
            args.includes,
            args.output,
        )
        if not args.quiet:
            print("Built:", out_path)


if __name__ == "__main__":
    main()
