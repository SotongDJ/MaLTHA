# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

MaLTHA (Markdown Language with TOML/HTML Hybrid Annotation) is a Python-based static site generator that converts Markdown/HTML content with TOML frontmatter into a deployable static website (targeting GitHub Pages). It uses a two-phase pipeline: content-to-JSON (`Convertor`), then JSON-to-HTML (`Generator`).

## Running the Generator

```bash
python -m MaLTHA              # Full run (removes and rebuilds docs/)
python -m MaLTHA --skip       # Skip initialization (skip clearing docs/)
python -m MaLTHA --debug      # Debug mode (disables base_url substitution)
```

Install dependencies:
```bash
pip install rtoml markdown2 Pygments
# or
pip install MaLTHA
```

There are no automated tests. Validation is done by running the generator against `_testrun/testcore/` and inspecting output in `docs/`.

To test with the local (development) copy rather than the pip-installed version:
```bash
cd _testrun/testcore && PYTHONPATH=/path/to/MaLTHA python -m MaLTHA
```

## Pipeline Architecture

The generation pipeline is orchestrated in `__main__.py` in six steps:

1. **Init**: Delete `docs/` via `shutil.rmtree()`, copy `static_files/` → `docs/` via `shutil.copytree()`
2. **Cleanup**: Delete `mid_files/` (intermediate JSON)
3. **Template loading** (`database.py` — `Formator`): Parse `config.toml`, load templates from `include_files/`, `layout_files/`, `page_files/`
4. **Content conversion** (`convert.py` — `Convertor`): Read all content directories, extract TOML frontmatter, validate required fields, build relationships/categories/feeds, write JSON to `mid_files/`
5. **HTML generation** (`generate.py` — `Generator`): Read JSON from `mid_files/`, escape code blocks, render templates using Python `.format()`, write HTML to `docs/`

Intermediate state lives in `mid_files/*.json`: `base.json`, `post.json`, `categories.json`, `page.json`, `post_pos.json`.

## Content Format

Posts are `.md` or `.html` files with TOML frontmatter:

```
+++
title = "Post Title"
date = 2024-01-15
categories = ["tag1", "tag2"]
short = ["url-shortname"]   # used in URL generation
path = "optional/subpath"
+++

<!--break type:content format:md content-->
Markdown content (preview portion)

<!-- separator -->

This part only appears in full-post view, not in listing previews.
```

Required post fields: `title`, `date`, `categories`, `short`. Required page fields: `title`, `path`.

## URL Generation

For each post, the `Convertor` generates multiple URL variants from `categories` and `short` fields:
- `/category/date/short/`
- `/category/short/`
- `/date/short/`
- `/short/`
- `/post/short/`

Duplicate `short` IDs across posts cause a build error (unless `auto_fix_duplicate = true` in `config.toml`).

## Template System

Templates use Python `.format(**dict)` substitution. The `Generator` applies double-formatting (`.format(**dict).format(**dict)`) to support nested variable expansion. Content inside `<pre>` blocks is automatically escaped to prevent `{...}` patterns in code from being interpreted as placeholders.

Template types loaded from files:
- `include_*` files → inline snippets
- `layout_*` files → page layouts
- `format_*` / `page_*` files → page-level formats

## Expected Project Directory Structure

```
project/
├── config.toml          # Site-level settings
├── static_files/        # Assets copied verbatim to docs/
├── include_files/       # Template includes
├── layout_files/        # Page layouts
├── page_files/          # Static pages
├── <content-dir>/       # One or more content directories (posts)
└── docs/                # Generated output (gitignored)
```

Content directories are any directories not starting with `.` or `_`, not containing `_files`, and not named `docs`, `run`, or `mid_files`. Additional exclusions can be configured via `exclude_dirs` in `config.toml`.

## Key config.toml Settings

| Key | Purpose |
|-----|---------|
| `base_title` | Site name |
| `base_url` | Base URL (disabled in `--debug` mode) |
| `separator_preview` | String used as preview/full content separator |
| `paginate_format` | URL format for pagination (e.g. `/page/{num}`) |
| `paginate_number` | Posts per page |
| `exclude_dirs` | List of directory names to skip during content scanning |
| `auto_fix_duplicate` | Boolean; auto-rename duplicate post short IDs (default: false) |
| `timezone_offset` | UTC offset in hours (default: 8) |
| `timezone_name` | Display name for timezone (default: `UTC+{offset}`) |

## Packaging

Build system uses `pyproject.toml` with setuptools. Version is defined in both `pyproject.toml` and `version.txt`.

```bash
pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```

## Git Conventions

All commits must be GPG-signed with key `E7D638E713696D8C`:
```bash
git commit -S --gpg-sign=E7D638E713696D8C
```
