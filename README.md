# pyMoTH

- work as a parser and a static site generator 
- use Markdown format with TOML/HTML hybrid annotation
- written in Python

## Work

- Brief example
  - [SotongDJ/trth.nl](https://github.com/SotongDJ/trth.nl)
  - under "link" and "*_files" folders: example of TOML/HTML hybrid annotation
- Requirement
  - config.toml
  - python module
    - tomlkit
    - markdown2
  - git submodule
  - git ignore (optional)
  - github actions (optional)

## Setup git submodule

``` bash
git submodule add https://github.com/SotongDJ/pyMoTH.git run
git submodule set-branch --branch main run
git submodule update --init --recursive
git submodule update --remote --merge
cat run/version.txt
```

## Changelog

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

## Disclaimer

- pyMoTH still work in progess
- better to use with own fork
