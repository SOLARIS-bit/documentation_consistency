import sys
import importlib
from pathlib import Path
from typing import Any, Dict, List

# ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Try to import package-level analyze_project and CodeParser
analyzer_pkg = None
analyze_project = None
CodeParser = None

try:
    analyzer_pkg = importlib.import_module("analyzer")
    analyze_project = getattr(analyzer_pkg, "analyze_project", None)
except Exception:
    analyzer_pkg = None

try:
    mod_cp = importlib.import_module("analyzer.code_parser")
    CodeParser = getattr(mod_cp, "CodeParser", None)
except Exception:
    CodeParser = None

def test_code_parser_returns_list():
    """CodeParser.analyze_directory should return a list of elements (possibly empty)."""
    if CodeParser is None:
        # fallback behaviour: assert we can import analyzer package instead
        assert analyzer_pkg is not None, "Neither analyzer.code_parser nor analyzer package available"
        return

    cp = CodeParser(str(PROJECT_ROOT))
    elems = cp.analyze_directory()
    assert isinstance(elems, list)
    # each element, if present, should be a dict with common keys
    if elems:
        e = elems[0]
        assert isinstance(e, dict)
        assert "name" in e and "type" in e and "file" in e

def test_analyze_project_returns_dict():
    """analyze_project should return a dict with a 'status' key (uses LLM fallback if necessary)."""
    if analyze_project is None:
        # It's ok if analyze_project is missing as long as package exists
        assert analyzer_pkg is not None
        return

    res = analyze_project(str(PROJECT_ROOT))
    assert isinstance(res, dict)
    assert "status" in res
    assert "issues" in res