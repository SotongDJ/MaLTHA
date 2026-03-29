# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

MaLTHA is a Python-based static site generator that converts Markdown/HTML content with TOML frontmatter into a deployable static website (targeting GitHub Pages). It uses a hybrid annotation format and a 6-step pipeline.

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

There are no automated tests. Validation is done by running the generator and inspecting output in `docs/`.

## Pipeline Architecture

The generation pipeline is orchestrated in `__main__.py` in six steps:

1. **Init**: Delete `docs/`, copy `static_files/` → `docs/`
2. **Cleanup**: Delete `mid_files/` (intermediate JSON)
3. **Template loading** (`database.py` — `Formator`): Parse `config.toml`, load templates from `include_files/`, `layout_files/`, `page_files/`
4. **Content conversion** (`convert.py` — `Convertor`): Read all content directories, extract TOML frontmatter, build relationships/categories/feeds, write JSON to `mid_files/`
5. **HTML generation** (`generate.py` — `Generator`): Read JSON from `mid_files/`, render templates using Python `.format()`, write HTML to `docs/`

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

## URL Generation

For each post, the `Convertor` generates multiple URL variants from `categories` and `short` fields:
- `/category/date/short/`
- `/category/short/`
- `/date/short/`
- `/short/`
- `/post/short/`

Duplicate `short` IDs across posts cause an error.

## Template System

Templates use Python `.format(**dict)` substitution. The `Generator` applies double-formatting (`.format(**dict).format(**dict)`) to support nested variable expansion. Template files use a custom `<!--break type:... format:... content-->` delimiter parsed by `Formator`.

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

Content directories are any directories not starting with `.` or `_` and not named `static_files`, `include_files`, `layout_files`, `page_files`, `mid_files`, or `docs`.

## Key config.toml Settings

| Key | Purpose |
|-----|---------|
| `base_title` | Site name |
| `base_url` | Base URL (disabled in `--debug` mode) |
| `separator_preview` | String used as preview/full content separator |
| `paginate_format` | URL format for pagination (e.g. `/page/{num}`) |
| `paginate_number` | Posts per page |
