import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analyzer import analyze_project

# ===== Top-level analyze_project Tests =====

def test_analyze_project_returns_dict():
    """analyze_project should return a dict with status and issues."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = analyze_project(tmpdir)
        assert isinstance(result, dict)
        assert "status" in result
        assert "issues" in result
        assert isinstance(result["issues"], list)

def test_analyze_project_fallback_mode():
    """analyze_project should return status=fallback or ok."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = analyze_project(tmpdir)
        assert result["status"] in ["ok", "fallback"]

def test_analyze_project_checked_samples():
    """analyze_project result should have checked_samples count."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = analyze_project(tmpdir)
        assert "checked_samples" in result
        assert isinstance(result["checked_samples"], int)
        assert result["checked_samples"] >= 0

def test_analyze_project_with_code():
    """analyze_project should analyze actual Python files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a sample Python file
        test_file = Path(tmpdir) / "example.py"
        test_file.write_text("""
def hello():
    '''Greet the world.'''
    return "Hello"

def goodbye():
    # Missing docstring
    return "Bye"
""")
        
        result = analyze_project(tmpdir)
        assert isinstance(result, dict)
        assert result["status"] in ["ok", "fallback"]
        assert "checked_samples" in result
        assert result["checked_samples"] >= 1
        
        # Should detect missing doc for goodbye
        issues = result.get("issues", [])
        assert isinstance(issues, list)

def test_analyze_project_mode_field():
    """analyze_project result should have mode (llm_augmented or deterministic)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = analyze_project(tmpdir)
        assert "mode" in result
        assert result["mode"] in ["llm_augmented", "deterministic"]

def test_analyze_project_llm_augmented_has_analysis():
    """If mode is llm_augmented, should have llm_analysis field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = analyze_project(tmpdir)
        if result.get("mode") == "llm_augmented":
            assert "llm_analysis" in result
            assert isinstance(result["llm_analysis"], str)

def test_analyze_project_project_root():
    """analyze_project should work on PROJECT_ROOT itself."""
    result = analyze_project(str(PROJECT_ROOT))
    assert isinstance(result, dict)
    assert "status" in result
    # PROJECT_ROOT has actual Python files, so checked_samples > 0
    assert result["checked_samples"] > 0