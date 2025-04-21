# MaLTHA Documentation

## Table of Contents
- [Overview](#overview)
- [Disclaimer](#disclaimer)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Project Structure](#project-structure)
- [Content Format](#content-format)
- [Site Configuration](#site-configuration)
- [Component Modules](#component-modules)
- [Workflow Steps](#workflow-steps)
- [Advanced Features](#advanced-features)
- [Example Site Setup](#example-site-setup)
- [Notes for Developers](#notes-for-developers)
- [Changelog](#changelog)

## Overview

MaLTHA is a static site generator that uses Markdown format with TOML/HTML hybrid annotation. It converts various file formats into a static website, optimized for GitHub Pages.

## Disclaimer
- MaLTHA still work in progess

## Installation

Install MaLTHA using pip:

```bash
pip install MaLTHA
```

### Dependencies

MaLTHA requires the following dependencies:
- rtoml
- markdown2
- Pygments (required for code highlighting in markdown)

## Basic Usage

MaLTHA works by transforming your content files into a static website with the following steps:

1. **Configuration**: Set up your site settings in `config.toml`
2. **Content Creation**: Write your content in Markdown or HTML with special frontmatter
3. **Generation**: Run MaLTHA to convert your content to a static site

### Command-Line Options

```bash
python -m MaLTHA [options]
```

Options:
- `--skip`: Skip the cleanup and initialization steps (steps 1 and 2)
- `--debug`: Run in debug mode (disables base URL)

## Project Structure

MaLTHA expects the following directory structure:

```
project/
├── config.toml              # Site configuration
├── static_files/            # Static assets to be copied to output
├── include_files/           # Includes for templates
├── layout_files/            # Layout templates
├── page_files/              # Individual page content
├── [content_directories]/   # Post content directories
└── docs/                    # Output directory (for GitHub Pages)
```

## Content Format

MaLTHA uses a hybrid format combining TOML frontmatter with HTML/Markdown content. Each content file should follow this structure:

```
+++
# TOML header
title = "Title of the page"
date = "2023-01-01T12:00:00+08:00"
categories = ["category1", "category2"]
short = ["short-id"]
+++

<!--break type:content format:md content-->
Content in Markdown format goes here.

You can use a separator to divide content between preview and full content:

<!-- separator -->

This part only shows in the full content view.
```

### Header Fields

- `title`: Page/post title
- `date`: Publication date (ISO format with timezone)
- `categories`: List of categories
- `short`: List of short identifiers (URLs)
- `path`: List of URL paths (for pages)
- `skip`: Optional, can be set to "content" or "list"
- `layout`: Optional layout template to use
- `base`: Optional base template
- `frame`: Optional frame template

## Site Configuration

The `config.toml` file configures the overall site. Example configuration:

```toml
base_title = "Site Title"
base_url = "https://yourusername.github.io"
separator_preview = "<!-- separator -->"
read_more = "Read more →"
read_original = "Read original →"
category_preview = "Posts in category: {0}"
paginate_format = "/page/{num}"
paginate_number = 5
```

## Component Modules

### Convertor

The `Convertor` class in `convert.py` handles the transformation of source files into JSON format:

- Reads content files from various directories
- Parses TOML/HTML/Markdown hybrid files
- Generates necessary metadata for posts, pages, and categories
- Outputs processed data as JSON files in the `mid_files` directory

### Formator

The `Formator` class in `database.py` handles:

- Loading site configuration from `config.toml`
- Parsing template files from include and layout directories
- Converting Markdown to HTML using markdown2
- Storing templates and configurations for other modules

### Generator

The `Generator` class in `generate.py` creates the final HTML pages:

- Consumes JSON data from the `mid_files` directory
- Applies templates to data
- Generates HTML files for posts, pages, categories, and pagination
- Creates the final directory structure in the `docs` folder

## Workflow Steps

When running `python -m MaLTHA`, the following steps are executed:

1. Remove the `docs` directory (if exists and `--skip` is not used)
2. Copy static files to `docs` (if `--skip` is not used)
3. Remove the `mid_files` directory
4. Load includes and layouts
5. Convert content files into JSON:
   - Process posts
   - Process categories
   - Generate relationships between posts
   - Process feed/atom data
   - Process pages
   - Output all data as JSON
6. Generate HTML pages:
   - Generate post pages
   - Generate static pages
   - Generate category pages
   - Generate pagination if configured

## Advanced Features

### Categories

MaLTHA automatically generates category pages and relationships between posts. You can customize their appearance through templates.

### Pagination

MaLTHA supports pagination for the main index page. Configure it using:

```toml
paginate_format = "/page/{num}"  # URL format for pagination
paginate_number = 5              # Posts per page
```

### Custom Templates

Templates use Python's string formatting (`{}`) syntax:

- `layout_default`: Base layout template
- `layout_post`: Post template
- `layout_page`: Page template
- `layout_category`: Category template
- `layout_pagination`: Pagination template

## Example Site Setup

1. Create config.toml with your site settings
2. Create content directories and files
3. Run `python -m MaLTHA` to generate the site
4. The output will be in the `docs` directory, ready for GitHub Pages

## Notes for Developers

- The code uses Python's `pathlib` for file operations
- Python 3.7+ is recommended
- TOML is used for configuration and metadata
- The generated site is designed for GitHub Pages hosting

## Changelog

- v0.3.2
  - add sorting to tag ordering
- v0.3.1
  - modified for the modulization
- v0.3.0 
  - release on PyPI
- v0.2.10
  - add "tables" into markdown2 extras
- v0.2.9
  - use rtoml instead of tomlkit
- v0.2.8
  - add "git submodule set-branch" to README and pyMoTH.yml
- v0.2.7
  - use fenced-code-blocks (markdown2)
- v0.2.6
  - adjust code for PEP (pylint)
- v0.2.5
  - fix canonical_url in categories and pagination
- v0.2.4
  - extend support of opengraph meta tag and add validator for trth.nl
- v0.2.3
  - change default setting (pyMoTH.yml)
