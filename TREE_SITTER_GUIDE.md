# Multi-Language Support with Tree-Sitter

## Overview

The documentation analyzer now supports **multiple programming languages** using tree-sitter:

- ✅ **Python** (.py)
- ✅ **Java** (.java)
- ✅ **C** (.c, .h)
- ✅ **C++** (.cc, .cpp, .cxx, .h, .hpp)
- ✅ **Go** (.go)
- ✅ **JavaScript** (.js, .jsx)
- ✅ **TypeScript** (.ts, .tsx)
- ✅ **Rust** (.rs)
- ✅ **C#** (.cs)
- ✅ **Ruby** (.rb)
- ✅ **PHP** (.php)

## Installation

### 1. Install Tree-Sitter

```bash
pip install -r requirements.txt
```

### 2. Install Language Libraries

Run the automated setup script:

```bash
python setup_tree_sitter.py
```

Or install manually:

```bash
# Install all language bindings
pip install tree-sitter-python tree-sitter-java tree-sitter-c tree-sitter-cpp \
            tree-sitter-go tree-sitter-javascript tree-sitter-typescript \
            tree-sitter-rust tree-sitter-c-sharp tree-sitter-ruby tree-sitter-php
```

### 3. Linux-specific (Ubuntu/Debian)

Ensure build tools are installed:

```bash
sudo apt-get install build-essential
```

### 4. macOS-specific

Ensure Xcode Command Line Tools are installed:

```bash
xcode-select --install
```

## Usage

### Analyzing Multi-Language Projects

Simply upload a ZIP file containing code in multiple languages:

```bash
streamlit run app.py
```

The analyzer will:
1. **Auto-detect** all supported languages
2. **Extract** functions, classes, methods from all files
3. **Compare** with documentation
4. **Generate** a comprehensive report

### Example Output

The PDF report will show:
- **Languages Found**: Python, Java, Go
- **Statistics**: Total elements, classes, functions, methods
- **Issues**: Missing documentation, inconsistent parameters
- **Language-specific Analysis**: Per-language breakdown

## How It Works

### TreeSitterParser Class

Located in `analyzer/tree_sitter_parser.py`:

```python
from analyzer.tree_sitter_parser import TreeSitterParser

parser = TreeSitterParser(project_dir="/path/to/project")
elements = parser.analyze_directory()

# Returns list of code elements:
# [
#   {
#     "name": "MyClass",
#     "type": "class",
#     "file": "src/main.java",
#     "line": 42,
#     "language": "java",
#     "doc": "Documentation string..."
#   },
#   ...
# ]
```

### Supported Element Types

- **class**: Class/struct definitions
- **function**: Top-level functions
- **method**: Class methods
- **version**: Version strings (Python)

### Fallback Behavior

If tree-sitter analysis fails, the system automatically falls back to the Python-only AST parser for `.py` files.

## Architecture

```
analyzer/
├── code_parser.py           # Python AST parser (legacy)
├── tree_sitter_parser.py    # Multi-language parser (NEW)
├── doc_parser.py            # Documentation parser
└── comparator.py            # Comparison logic

project_analyzer.py          # Main analyzer (updated for multi-language)
```

## Performance

- **Tree-sitter**: Faster C-based parsing, supports 11+ languages
- **Python AST**: Slower but more stable for Python
- **Fallback**: Automatic if tree-sitter unavailable

## Troubleshooting

### Issue: "tree-sitter not installed"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "No parser available for language X"
**Solution**: The language library might not be installed
```bash
python setup_tree_sitter.py
```

### Issue: "Import errors on macOS"
**Solution**: Install Xcode Command Line Tools
```bash
xcode-select --install
```

### Issue: "Build failures on Linux"
**Solution**: Install build essentials
```bash
sudo apt-get install build-essential python3-dev
```

## Adding New Languages

To add support for a new language:

1. Install the tree-sitter binding:
   ```bash
   pip install tree-sitter-<language>
   ```

2. Add to `LANGUAGE_EXTENSIONS` in `TreeSitterParser`

3. Implement extraction method `_extract_<language>_elements()`

4. Update documentation

Example for a new language "lua":

```python
def _extract_lua_elements(self, node, source_code: bytes, filepath: Path, language: str):
    """Extract Lua functions and tables."""
    results = []
    # Implementation...
    return results
```

## API Reference

### TreeSitterParser

#### `__init__(project_dir: str | Path)`
Initialize parser for a project directory.

#### `analyze_file(filepath: str | Path) -> List[Dict[str, Any]]`
Parse a single file and extract code elements.

#### `analyze_directory() -> List[Dict[str, Any]]`
Analyze all supported code files in project directory.

#### `get_language_for_file(filepath: Path) -> Optional[str]`
Determine the programming language based on file extension.

## Examples

### Python Project
```bash
# Upload python_project.zip
# Automatically detected and analyzed
```

### Multi-Language Project
```bash
# Upload mixed_project.zip containing:
# - src/main.java (Java)
# - src/utils.py (Python)
# - src/helpers.go (Go)
# - src/config.js (JavaScript)
#
# All analyzed together with consistent metrics
```

### CI/CD Integration

```python
from project_analyzer import analyze_project

result = analyze_project(
    project_path="/path/to/extracted/project",
    project_name="MyProject"
)

print(f"Languages found: {result['languages']}")
print(f"Total issues: {len(result['issues'])}")
print(f"Coverage: {result['stats']}")
```

## Dependencies

```
tree-sitter>=0.20.0
tree-sitter-languages>=1.10.2

# Individual language bindings:
tree-sitter-python
tree-sitter-java
tree-sitter-c
tree-sitter-cpp
tree-sitter-go
tree-sitter-javascript
tree-sitter-typescript
tree-sitter-rust
tree-sitter-c-sharp
tree-sitter-ruby
tree-sitter-php
```

## Notes

- Each language uses its official tree-sitter grammar
- Parsing is done in pure Python (no external processes)
- Memory usage is proportional to project size
- Supports nested classes and methods
- Filters out test files, private methods, and common utilities

## License

This implementation uses tree-sitter grammars which are typically MIT licensed.
