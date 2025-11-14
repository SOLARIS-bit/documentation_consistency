# Documentation Consistency Tool

A small toolkit to analyze and improve the consistency between code and documentation in Python projects.  
Designed to run on ARM64 environments (e.g., Chromebook) with minimal dependencies and to gracefully fall back when optional LLM integrations are not available.

---

## Table of contents

- [Overview](#overview)
- [Features](#features)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quickstart](#quickstart)
- [Modules & API](#modules--api)
- [Development notes (ARM64 / VSCode)](#development-notes-arm64--vscode)
- [Testing](#testing)
- [CI / GitHub Actions (suggested)](#ci--github-actions-suggested)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project scans a codebase to detect documentation gaps and suggests improvements. When LangChain + OpenAI are available, it uses an LLM to generate higher-quality suggestions. Otherwise, it uses deterministic fallbacks so tests and editors (Pylance) behave predictably.

Goals:
- Detect functions/classes without documentation or with mismatched/incorrect docs
- Offer text improvement suggestions (via LLM when available)
- Produce simple visual summaries (PNG) for reports
- Be usable and testable on ARM64 with minimal dependencies

---

## Features

- Static parsing of Python files to extract signatures and docstrings
- Documentation extraction (README, rst/md) and lightweight matching
- LLM-backed suggestions (optional): uses `langchain.llms.OpenAI` when available
- Deterministic fallbacks so project works without LLM packages installed
- Helpers to generate synthetic data (fallback when synthcity is not installed)

---

## Project structure

```
documentation_consistency/
├── analyzer/
│   ├── code_parser.py        # parse Python files
│   ├── doc_parser.py         # read documentation files
│   ├── comparator.py         # compare code vs docs
├── generator/
│   ├── text_suggester.py     # LLM + fallback suggestions
│   ├── visual_creator.py     # small PNG summary generator
├── analyzer.py               # top-level analyzer using langchain (optional)
├── app.py                    # example glue demonstrating usage
├── data_generator.py         # synthetic data generator with fallback
├── main.py                   # CLI entry (if provided)
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Requirements

Minimum:
- Python 3.8+
- pip

Recommended (ARM64-friendly minimal set):
- langchain==1.0.2  (optional — for LLM features)
- pillow             (for generating visuals)

Example `requirements.txt` minimal:
```
langchain==1.0.2
pillow
```
Note: LLM packages (openai SDK, heavy ML libraries) are optional. The code provides runtime fallbacks if LangChain/OpenAI are not installed.

---

## Installation

1. Create and activate a venv:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
# or minimal:
pip install langchain==1.0.2 pillow
```

3. (Optional) Set OpenAI API key for LLM features:
```bash
export OPENAI_API_KEY="sk_..."
```

4. Open the project in VSCode and select the `.venv` interpreter (Command Palette → Python: Select Interpreter).

---

## Configuration

- OPENAI_API_KEY — required to use the OpenAI LLM via LangChain if you want model suggestions.
- If you do not provide an API key or LangChain is not installed, modules will use fallback behavior that returns deterministic suggestions.

---

## Quickstart

Run the example application:
```bash
python app.py
```

Typical output:
- Analyzer result summary printed to console
- Example text suggestion printed (fallback or LLM)
- Visual created (path printed) when visual generator is available

---

## Modules & API

High-level functions you can call from scripts:

- analyze_project(project_path: str) -> dict | str  
  Top-level analyzer (in `analyzer.py`). Uses LLM when available; fallback deterministic result otherwise.

- suggest_text_improvements(doc_text: str) -> dict | str  
  In `generator/text_suggester.py`. Uses LangChain/OpenAI when available; returns a fallback summary otherwise.

- create_visual(summary: str) -> str  
  In `generator/visual_creator.py`. Generates a PNG summary and returns the file path.

- generate_synthetic_data() -> dict  
  In `data_generator.py`. Returns example code/docs and synthetic_data field; uses synthcity if present, otherwise returns a small internal example.

Examples:
```python
from analyzer import analyze_project
from generator.text_suggester import suggest_text_improvements

res = analyze_project("./my_project")
print(res)

suggestion = suggest_text_improvements("Function does x but doc is missing")
print(suggestion)
```

---

## Development notes (ARM64 / VSCode)

- If VSCode Pylance reports missing imports but you have packages installed, ensure the selected interpreter matches the environment where you installed packages.
  - `which python`
  - `python -m pip show langchain`
  - In VSCode: Command Palette → Python: Select Interpreter → choose `.venv`

- The code uses dynamic import (`importlib`) and local fallbacks so tests and the language server remain stable even if optional deps are missing.

- If you face DNS / pip network errors (e.g., "Temporary failure in name resolution"):
  - Check `/etc/resolv.conf`
  - Ensure network connectivity
  - Use `pip install --no-cache-dir <pkg>` when needed

---

## Testing

Add tests under `tests/` (examples):
- `tests/test_analyzer.py` — unit tests for fallback flows
- `tests/test_text_suggester.py` — tests for fallback suggestion

Run tests with pytest:
```bash
pip install pytest
pytest -q
```

The project includes fallback stubs for environments without analyzer submodules; tests should assert both LLM and fallback behaviors.

---

## CI / GitHub Actions (suggested)

Add `.github/workflows/python.yml` to run tests on push/PR:
- Install minimal deps
- Run `pytest`
- Optionally run linting (flake8/black)

Example (brief):
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: python-version: "3.10"
      - run: python -m venv .venv && . .venv/bin/activate
      - run: pip install -r requirements.txt
      - run: pip install pytest
      - run: pytest -q
```

---

## Troubleshooting

- "Import ... could not be resolved" in VSCode:
  - Ensure you selected the correct interpreter
  - Restart the language server / reload the window
  - Use `python -m pip install <package>` inside the selected venv

- "remote: Repository not found" on git push:
  - Check remote URL `git remote -v`
  - Remove old remote: `git remote remove origin`
  - Add correct remote and push

- LLM invocation errors:
  - Confirm `OPENAI_API_KEY` is set
  - Check LangChain and OpenAI client versions
  - Fallback behavior will still return useful deterministic results

---

## Contributing

Contributions welcome. Suggested workflow:
1. Fork repository
2. Create a feature branch
3. Add tests for new behavior
4. Open a PR with clear description

Please follow small, focused PRs and add unit tests for logic changes.

---

## License

MIT — see LICENSE file.

---
