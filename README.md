# MaLTHA

**Markdown Language with TOML/HTML Hybrid Annotation**

A static site generator that converts Markdown and HTML content annotated with TOML frontmatter into a deployable static website. Designed for GitHub Pages.

## Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration Reference](#configuration-reference)
- [Content Format Specification](#content-format-specification)
- [Template System](#template-system)
- [Pipeline Detail](#pipeline-detail)
- [Module Reference](#module-reference)
- [URL Generation](#url-generation)
- [Deployment](#deployment)
- [Changelog](#changelog)
- [License](#license)

---

## Architecture

MaLTHA operates as a six-step pipeline that transforms source content into static HTML through an intermediate JSON representation. This two-phase design (content to JSON, then JSON to HTML) decouples content parsing from template rendering.

```
Source Files                    Intermediate JSON             Output HTML
============                    =================             ===========

config.toml ──┐
              │
include_files ┤  Step 4         mid_files/
layout_files  ├──(Formator)──▶  base.json        Step 6
page_files    │                  post.json      ──(Generator)──▶  docs/
              │  Step 5          categories.json                  ├── index.html
content dirs ─┴──(Convertor)──▶  page.json                       ├── category/
                                 post_pos.json                    ├── post/...
static_files ────(Step 1-2)──────────────────────────────────────▶└── (assets)
```

### Design Decisions

**Python `str.format()` as template engine.** Templates use Python's built-in string formatting via `.format(**dict)`. The `Generator` applies two consecutive format passes to support nested variable expansion (a template value can itself contain `{placeholders}`). This is intentionally simple and avoids a Jinja2/Mako dependency, at the cost of requiring `{{`/`}}` escaping for literal braces in templates.

**JSON as intermediate format.** The `mid_files/*.json` layer allows the content conversion step (`Convertor`) and the HTML generation step (`Generator`) to operate independently. This makes it possible to inspect or manipulate the intermediate data externally.

**Convention-over-configuration directory scanning.** Content directories are auto-discovered by scanning top-level directories, excluding those that start with `.` or `_`, contain `_files`, or are named `docs`, `run`, or `mid_files`. An `exclude_dirs` list in `config.toml` provides explicit exclusion for polyglot repositories.

---

## Installation

```bash
pip install MaLTHA
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `rtoml` | TOML parsing for config and frontmatter |
| `markdown2` | Markdown-to-HTML conversion |
| `Pygments` | Syntax highlighting in fenced code blocks |

### From Source

```bash
git clone https://github.com/SotongDJ/MaLTHA.git
cd MaLTHA
pip install -e .
```

---

## Usage

```bash
python -m MaLTHA              # Full build: clear docs/, rebuild everything
python -m MaLTHA --skip       # Skip steps 1-2: keep existing docs/, regenerate from content
python -m MaLTHA --debug      # Debug mode: disable base_url substitution for local preview
```

| Flag | Effect |
|------|--------|
| `--skip` | Skips deletion of `docs/` and re-copying of `static_files/`. Useful for iterative content changes. |
| `--debug` | Sets `base_url` to empty string so all generated URLs are root-relative, enabling local file browsing. |

There are no automated tests. Validation is done by running the generator and inspecting output in `docs/`.

---

## Project Structure

MaLTHA expects the following layout in the working directory:

```
project/
├── config.toml              # Site-level configuration
├── static_files/            # Assets copied verbatim to docs/ (CSS, JS, images)
├── include_files/           # Template includes (reusable HTML snippets)
├── layout_files/            # Page layout templates
├── page_files/              # Static page definitions
├── <content-dir>/           # One or more content directories (posts)
│   ├── post-one.md
│   └── post-two.html
├── mid_files/               # Generated intermediate JSON (gitignored)
└── docs/                    # Generated output (gitignored, deploy target)
```

### Directory Discovery Rules

A top-level directory is treated as a content directory if all of the following are true:

1. It is a directory (not a file)
2. Its name does not start with `.` or `_`
3. Its name does not contain `_files`
4. Its name is not `docs`, `run`, or `mid_files`
5. Its name is not listed in the `exclude_dirs` config option

---

## Configuration Reference

The `config.toml` file defines site-wide settings. All values are passed through the template system as format variables.

### Required Settings

| Key | Type | Description |
|-----|------|-------------|
| `base_title` | string | Site name, used in `<title>` and template composition |
| `base_url` | string | Base URL for the deployed site (e.g., `"https://user.github.io/repo"`) |
| `separator_preview` | string | HTML comment used to split preview/full content (e.g., `"<!--excerpt-->"`) |
| `read_more` | string | Link text shown when post has preview+full content |
| `read_original` | string | Link text shown when post has no preview split |
| `category_preview` | string | Format string for category description (receives one `{}` argument) |
| `paginate_format` | string | URL pattern for pagination pages (e.g., `"/page/{num}"`) |
| `paginate_number` | integer | Number of posts per paginated page |

### Optional Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `exclude_dirs` | list of strings | `[]` | Directories to exclude from content scanning |
| `auto_fix_duplicate` | boolean | `false` | Auto-rename duplicate post short IDs instead of halting |
| `timezone_offset` | number | `8` | UTC offset in hours for generated timestamps |
| `timezone_name` | string | `"UTC+{offset}"` | Display name for the timezone |

Any additional keys in `config.toml` are available as template variables throughout the system.

---

## Content Format Specification

MaLTHA uses a hybrid annotation format called **ToMH** (TOML Markdown HTML). Content files combine TOML frontmatter with annotated content blocks.

### Post Format

Posts are `.md` or `.html` files in content directories:

```
+++
title = "Post Title"
date = 2024-01-15
categories = ["tag1", "tag2"]
short = ["url-shortname"]
+++

<!--break type:content format:md content-->
This is the preview content shown in listings.

<!-- separator -->

This content only appears in the full post view.
```

#### Required Post Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Post title |
| `date` | date/datetime | Publication date (ISO format) |
| `categories` | list of strings | Category tags |
| `short` | list of strings | URL short identifiers (first is canonical) |

#### Optional Post Fields

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Override URL subpath |

### Page Format

Pages are files in `page_files/`:

```
+++
title = "Page Title"
path = ["/about/"]
+++

<!--break type:content format:md content-->
Page content here.
```

#### Required Page Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Page title |
| `path` | list of strings | URL paths for this page |

#### Optional Page Fields

| Field | Type | Description |
|-------|------|-------------|
| `skip` | string | `"content"` to skip content generation, `"list"` to hide from sidebar |
| `layout` | string | Name of a layout template to apply |
| `base` | string | Name of a base template to use instead of `layout_default` |
| `frame` | string | Name of a frame template |

### Block Annotation Syntax

Content blocks are delimited by HTML comments with the format:

```
<!--break type:<type> format:<format> content-->
```

| `type` value | Behavior |
|--------------|----------|
| `header` | Content is parsed as TOML frontmatter |
| `content` | Content is the main body |
| Other values | Content is stored as a named frame/section |

| `format` value | Behavior |
|----------------|----------|
| `md` | Content is converted from Markdown to HTML (with fenced-code-blocks and tables) |
| Other values | Content is kept as-is (HTML or plain text) |

For non-header, non-content blocks, an additional `title:<name>` attribute names the section.

---

## Template System

Templates use Python `str.format()` substitution. Any `{key}` in a template is replaced by the corresponding value from the rendering context.

### Template Types

| Prefix | Source Directory | Purpose |
|--------|-----------------|---------|
| `include_*` | `include_files/` | Reusable inline HTML snippets |
| `layout_*` | `layout_files/` | Page structure templates |
| `format_*` | `page_files/`, `layout_files/` | Formatting templates for components |

### Key Layout Templates

| Template Name | Used For |
|---------------|----------|
| `layout_default` | Outer HTML wrapper for all pages |
| `layout_post` | Post content layout |
| `layout_page` | Static page content layout |
| `layout_category` | Category listing layout |
| `layout_pagination` | Paginated index layout |

### Multi-Pass Rendering

The `Generator` applies `.format()` in two passes (three for pages with `frame` or `layout` templates). This allows template values to themselves contain `{placeholders}` that resolve in the second pass.

To include a literal `{` or `}` in template output, use `{{` and `}}`. These are resolved in the final cleanup step.

### Code Block Protection

Content inside `<pre>` HTML blocks is automatically escaped before format passes. This prevents `{...}` patterns in code examples (JSON, Python, Go, etc.) from being interpreted as template placeholders.

---

## Pipeline Detail

### Step 1: Initialize Output Directory

Deletes the `docs/` directory and copies `static_files/` to `docs/`. Uses `shutil.rmtree()` and `shutil.copytree()` for cross-platform compatibility. Skipped with `--skip`.

### Step 2: Clean Intermediate Files

Deletes the `mid_files/` directory.

### Step 3: Load Templates (`Formator.load()`)

Parses all template files from `include_files/`, `layout_files/`, and `page_files/` using the ToMH block annotation format. Builds the `structure` dictionary mapping template names to their content strings.

### Step 4: Convert Content (`Convertor`)

Processes content in this order:

1. **`post()`** — Scan content directories, parse each `.md`/`.html` file, extract frontmatter, validate required fields, compute URL variants, build post data structures.
2. **`category()`** — Aggregate posts by category, generate category member listings.
3. **`relate()`** — Compute related posts for each post based on shared categories (up to 3 most recent).
4. **`atom()`** — Build Atom feed entries and post preview/full container HTML.
5. **`page()`** — Parse page files, validate frontmatter, build page data structures and sidebar listings.
6. **`output()`** — Write all data structures to `mid_files/*.json`.

### Step 5: Generate HTML (`Generator`)

Reads JSON from `mid_files/` and renders final HTML:

1. **`post()`** — For each post, merge template+config+post data, render through `layout_default`, write to all URL paths.
2. **`page()`** — For each page, render with appropriate layout, activate sidebar entry, write to URL paths.
3. **`category()`** — For each category, render category listing page.
4. **`pagination()`** — Split post list into pages, render with navigation buttons.

### Intermediate JSON Files

| File | Content |
|------|---------|
| `base.json` | Merged config + computed site-wide data (category lists, post lists, atom content) |
| `post.json` | Array of post data objects |
| `post_pos.json` | Map of `short_canonical` to position index |
| `categories.json` | Map of category name to category data (members, URLs, rendered sections) |
| `page.json` | Map of page title to page data |

---

## Module Reference

### `database.py` — `Formator`

| Method | Description |
|--------|-------------|
| `__init__()` | Loads `config.toml` into `self.base` |
| `parse(input_str)` | Parses a ToMH string into a dict of `{header, content, frame, ...}` |
| `load()` | Parses all template files and populates `self.structure` |
| `oneline(input_str)` | Collapses a string to one line (removes newlines and 4-space indentation) |
| `export()` | Exports `self.structure` to `mid_files/structure.toml` |

### `convert.py` — `Convertor`

| Method | Description |
|--------|-------------|
| `__init__(bu_b, fmt)` | Initialize with base_url toggle and Formator instance |
| `is_target(folder)` | Returns whether a directory should be scanned for content |
| `validate_post_header(head_d, file_path)` | Validates required frontmatter fields, raises with file path on error |
| `post()` | Process all post files from content directories |
| `check_post()` | Detect duplicate short IDs; halt or auto-fix based on config |
| `category()` | Build category data structures |
| `relate()` | Compute related post lists |
| `atom()` | Build Atom feed and preview containers |
| `page()` | Process page files |
| `output()` | Write all JSON to `mid_files/` |

### `generate.py` — `Generator`

| Method | Description |
|--------|-------------|
| `__init__(fmt)` | Load JSON data, configure timezone from config |
| `escape_code_blocks(html_str, passes)` | Escape `{`/`}` in `<pre>` blocks to survive N `.format()` passes |
| `post()` | Render and write all post HTML files |
| `page()` | Render and write all page HTML files |
| `category()` | Render and write all category HTML files |
| `pagination()` | Render and write paginated index pages |

---

## URL Generation

For each post, `Convertor` generates multiple URL paths from the `categories` and `short` fields. Given `categories = ["cat1", "cat2"]`, `short = ["my-post"]`, and `date = 2024-01-15`:

| Pattern | Example |
|---------|---------|
| `/{categories}/{date}/{short}/` | `/cat1/cat2/2024/01/15/my-post/` |
| `/{categories}/{short}/` | `/cat1/cat2/my-post/` |
| `/{date}/{short}/` | `/2024/01/15/my-post/` |
| `/{short}/` | `/my-post/` |
| `/post/{short}/` | `/post/my-post/` |

The canonical URL is `/{date}/{short[0]}/`. All paths receive the same HTML content via directory-based routing (`path/index.html`).

Duplicate `short[0]` values across posts cause a build error unless `auto_fix_duplicate = true` is set in `config.toml`.

For pages, paths ending in a file extension (e.g., `/atom.xml`) are written as flat files; all others generate `index.html` inside a directory.

---

## Deployment

### GitHub Pages with GitHub Actions

Copy `MaLTHA.yml` to `.github/workflows/` in your content repository:

```yaml
name: Deploy static content to Pages [MaLTHA]

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Install MaLTHA
        run: pip install MaLTHA
      - name: Generate site
        run: python3 -m MaLTHA
      - name: Setup Pages
        uses: actions/configure-pages@v2
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v1
        with:
          path: './docs'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v1
```

### Local Preview

```bash
python -m MaLTHA --debug
cd docs && python -m http.server 8000
```

---

## Changelog

### v0.4 (2026-03-30)

Robustness, portability, and configurability improvements.

- **Cross-platform file operations**: Replaced Unix-specific `subprocess.call(["rm",...])` / `subprocess.call(["cp",...])` with `shutil.rmtree()` / `shutil.copytree()`
- **Resource management**: All file reads now use `with open()` context managers instead of bare `open().read()`
- **Mutable default fix**: `Convertor` and `Generator` constructors no longer share a mutable `Formator()` default argument
- **Debug mode fix**: `--debug` now correctly clears `base_url` from the base data dictionary, preventing absolute URLs in local builds
- **Directory exclusion**: New `exclude_dirs` config option to exclude directories from content scanning, enabling safe use in polyglot repositories
- **Frontmatter validation**: Posts and pages with missing required TOML fields now raise errors with the file path. Files without a header block are skipped with a warning.
- **Duplicate detection**: `check_post()` now halts the build on duplicate post IDs. New `auto_fix_duplicate` config option for auto-renaming.
- **Code block protection**: `{` and `}` inside `<pre>` blocks are automatically escaped before template format passes, preventing crashes on technical documentation with code examples
- **Configurable timezone**: New `timezone_offset` and `timezone_name` config options (default: UTC+8)

### v0.3.2

- Add sorting to tag ordering

### v0.3.1

- Modified for modulization

### v0.3.0

- Release on PyPI

### v0.2.10

- Add "tables" into markdown2 extras

### v0.2.9

- Use rtoml instead of tomlkit

### v0.2.8

- Add "git submodule set-branch" to README and pyMoTH.yml

### v0.2.7

- Use fenced-code-blocks (markdown2)

### v0.2.6

- Adjust code for PEP (pylint)

### v0.2.5

- Fix canonical_url in categories and pagination

### v0.2.4

- Extend support of opengraph meta tag and add validator for trth.nl

### v0.2.3

- Change default setting (pyMoTH.yml)

---

## License

MaLTHA is licensed under the [GNU General Public License v3.0](LICENSE).
