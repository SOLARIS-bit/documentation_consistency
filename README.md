# 📚 Documentation Consistency Assistant

An AI-powered tool that verifies whether a project's documentation is consistent, complete, and up to date with its codebase. It automatically detects mismatches between code and documentation, and suggests fixes or generates missing documentation.

## 🎯 Features

- **Code Analysis**: Extracts functions, classes, methods, and docstrings from Python projects
- **Documentation Scanning**: Reads and analyzes Markdown and text documentation files
- **Consistency Checking**: Identifies undocumented functions, outdated descriptions, and parameter mismatches
- **Smart Suggestions**: Generates improvement proposals using LLM (OpenAI) or local heuristics
- **Visual Reports**: Creates HD PNG analysis summaries with metrics and scores
- **Architecture Diagrams**: Generates Mermaid diagrams showing project structure
- **Web Dashboard**: User-friendly Streamlit interface for easy interaction
- **CI/CD Ready**: GitHub Actions workflow for automated documentation checks

## 🚀 Quick Start

### Installation

**Prerequisites:**
- Python 3.11+
- pip or conda

**Option 1: Using pip (Standard)**
```bash
git clone https://github.com/yourusername/documentation_consistency.git
cd documentation_consistency
pip install -r requirements.txt
```

**Option 2: For ARM64 (Raspberry Pi, Apple Silicon)**
```bash
pip install -r requirements-arm64.txt
```

**Option 3: CI/CD Only (Minimal dependencies)**
```bash
pip install -r requirements-ci.txt
```

### Running the Web Dashboard

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Running the Demo

```bash
python demo.py
```

This analyzes the included `example_project/` and generates a sample report.

### Running Tests

```bash
pytest -v
```

## 📖 Usage

### Web Interface (Recommended)

1. Open the dashboard: `streamlit run app.py`
2. Upload your project as a ZIP file
3. (Optional) Upload additional documentation as ZIP
4. View the analysis summary
5. Download the visual report and suggested improvements

### Command Line

```python
from project_analyzer import analyze_project

result = analyze_project("/path/to/project")
print(f"Issues found: {len(result['issues'])}")
print(f"Status: {result['status']}")
```

## 🏗️ Architecture

```
┌──────────────────────────────────────┐
│   Web Interface (Streamlit - app.py) │
│   - File upload handling             │
│   - Report visualization             │
│   - Download management              │
└─────────────────┬────────────────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │ Project Analyzer    │  (project_analyzer.py)
        │ - Orchestrates flow │
        │ - LLM integration   │
        └──────────┬──────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
  ┌─────────┐ ┌─────────┐
  │  Code   │ │   Doc   │
  │ Parser  │ │ Parser  │
  └──┬──────┘ └─────┬───┘
    │              │
    └──────────────┘
                     │
                     ▼
            ┌────────────────┐
            │   Comparator   │
            │ - Matches code │
            │   vs. docs     │
            │ - Filters noise│
            └────────┬───────┘
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
   ┌─────────┐ ┌─────────┐ ┌──────────┐
   │  Text   │ │ Visual  │ │ Mermaid  │
   │Generator│ │ Creator │ │Generator │
   └─────────┘ └─────────┘ └──────────┘
```

## 📁 Project Structure

```
documentation_consistency/
├── analyzer/                          # Core analysis modules
│   ├── code_parser.py                 # Python code extraction
│   ├── doc_parser.py                  # Documentation parsing
│   └── comparator.py                  # Code vs. doc comparison
├── generator/                         # Report/suggestion generation
│   ├── text_suggester.py              # LLM-based suggestions
│   ├── visual_creator.py              # PNG report generation
│   └── mermaid_generator.py           # Diagram generation
├── tests/                             # Test suite
│   ├── test_modules.py
│   ├── test_analyzer.py
│   └── test_anlyzer_init.py
├── example_project/                   # Sample project for testing
│   ├── README.md                      # Intentionally incomplete
│   ├── math_utils.py
│   ├── student.py
│   └── teacher.py
├── app.py                             # Streamlit web dashboard
├── main.py                            # CLI entry point
├── demo.py                            # Demo script
├── project_analyzer.py                # Main analysis orchestrator
├── requirements.txt                   # Python dependencies
├── requirements-arm64.txt             # ARM-optimized dependencies
├── requirements-ci.txt                # CI/CD minimal dependencies
├── settings.json                      # Configuration
└── README.md                          # This file
```

## ⚙️ Configuration

Edit `settings.json` to customize:

```json
{
  "max_file_size_mb": 50,
  "max_issues_shown": 100,
  "exclude_dirs": ["tests", "venv", "docs", ".git"],
  "llm_model": "gpt-4o-mini",
  "llm_temperature": 0.1
}
```

## 🔌 API Integration

### OpenAI/LLM Configuration

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-..."
```

The assistant will use GPT-4o-mini by default for enhanced suggestions.

## 📊 Understanding the Report

### Health Score
- **90-100**: Documentation is well-maintained, highly consistent
- **70-89**: Minor gaps, mostly documented
- **50-69**: Significant inconsistencies, multiple missing docs
- **Below 50**: Major documentation overhaul needed

### Issue Types
- **MISSING_DOC_FUNCTION**: Function not described in documentation
- **MISSING_DOC_CLASS**: Class not documented
- **MISSING_DOC_METHOD**: Method missing from docs
- **INCONSISTENCY_PARAM**: Parameter names don't match documentation
- **VERSION_MISMATCH**: Code version differs from documented version

## 🧪 Testing

Run the test suite:
```bash
pytest -v                    # All tests
pytest tests/test_modules.py # Specific test file
pytest -k "parser"           # Filter by keyword
```

## 🔐 Security Considerations

- **File Upload Limits**: Max 50MB ZIP files by default
- **ZIP Bomb Detection**: Validates ZIP structure before extraction
- **Code Execution**: Never executes analyzed code, only parses AST
- **API Keys**: Never stored in code, use environment variables
- **Temporary Files**: All uploads cleaned up after analysis

## 🚀 CI/CD Integration

### GitHub Actions

Already configured in `.github/workflows/ci.yml`. Add a check to your workflow:

```yaml
- name: Check Documentation Consistency
  run: |
    python -m pytest
    python project_analyzer.py
```

### Generate Report as Artifact

```yaml
- name: Generate Report
  run: python demo.py
  
- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: doc-consistency-report
    path: output.png
```

## 📚 Examples

### Analyze a Local Project

```python
from project_analyzer import analyze_project

result = analyze_project("./my_project")
print(f"Found {len(result['issues'])} documentation issues")
for issue in result['issues'][:5]:
    print(f"  - {issue}")
```

### Generate Visual Report

```python
from generator.visual_creator import create_visual_summary

result = {"issues": [...], "checked_samples": 15, "status": "ok"}
output_path = create_visual_summary(result, "report.png")
print(f"Report saved to {output_path}")
```

### Get LLM Suggestions

```python
from generator.text_suggester import suggest_text_improvements

issues = ["Missing documentation for: process_data"]
suggestions = suggest_text_improvements("\n".join(issues))
print(suggestions)
```

## 🎓 How It Works

### 1. Code Extraction
- Uses Python's `ast` module to parse Python files
- Extracts functions, classes, methods, and docstrings
- Filters out test files and private methods
- Captures function parameters for consistency checking

### 2. Documentation Parsing
- Scans Markdown and text files
- Extracts section headers and content
- Builds searchable index of documented entities

### 3. Comparison
- Uses NLP similarity matching (embedding-based)
- Matches code entities with documentation
- Detects parameter mismatches
- Identifies version inconsistencies

### 4. Suggestion Generation
- **With LLM**: Uses OpenAI GPT-4o-mini for intelligent recommendations
- **Without LLM**: Uses local heuristics for ARM/offline environments
- Contextual advice based on project size (small vs. large library)

### 5. Report Generation
- Creates HD PNG visualization
- Generates Mermaid architecture diagrams
- Produces downloadable markdown snippets

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY="your-key-here"
```

### "ZIP extraction failed"
- File might be corrupted
- Size might exceed limit (50MB default)
- Try re-creating the ZIP file

### "No issues detected"
- Project documentation is well-maintained (good!)
- Or parser failed silently (check logs)

## 📈 Performance

- Small projects (<10 files): ~1-2 seconds
- Medium projects (10-100 files): ~5-15 seconds
- Large projects (>100 files): ~30+ seconds
## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Support for other languages (JS, Go, Rust, etc.)
- Multi-language documentation (EN/FR/ES)
- More visual diagram options
- Knowledge graph generation

## 📝 License

MIT License - see LICENSE file for details

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/documentation_consistency/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/documentation_consistency/discussions)

## 🔄 Version History

- **v2.0** (Jan 2026): Added Mermaid diagrams, improved logging
- **v1.0** (Dec 2025): Initial release with core functionality

---

**Made with ❤️ for better documentation practices**
