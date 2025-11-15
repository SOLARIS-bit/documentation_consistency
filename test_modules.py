import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analyzer.code_parser import CodeParser
from analyzer.doc_parser import DocumentationParser
from analyzer.comparator import Comparator
from generator.text_suggester import suggest_text_improvements
from generator.visual_creator import create_visual

# ===== CodeParser Tests =====

def test_code_parser_empty_directory():
    """CodeParser on truly empty dir should return empty list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cp = CodeParser(tmpdir)
        result = cp.analyze_directory()
        assert isinstance(result, list)
        assert len(result) == 0

def test_code_parser_analyze_file_with_function():
    """CodeParser should extract function docstrings."""
    # Create a temp file in PROJECT_ROOT for testing
    test_file = PROJECT_ROOT / "temp_test_module.py"
    test_file.write_text("""
def greet(name):
    '''Say hello to someone.'''
    return f"Hello {name}"

class Greeter:
    '''A greeter class.'''
    
    def greet_many(self, names):
        '''Greet multiple people.'''
        pass
""")
    
    try:
        cp = CodeParser(str(PROJECT_ROOT))
        result = cp.analyze_file(str(test_file))
        assert len(result) >= 2  # At least function + class
        
        func = [r for r in result if r["type"] == "function"]
        assert len(func) > 0
        assert func[0]["name"] == "greet"
        assert "Say hello" in func[0]["doc"]
        
        classes = [r for r in result if r["type"] == "class"]
        assert len(classes) > 0
        assert classes[0]["name"] == "Greeter"
        
    finally:
        test_file.unlink()

# ===== DocumentationParser Tests =====

def test_doc_parser_read_docs():
    """DocumentationParser should find and read docs."""
    dp = DocumentationParser(str(PROJECT_ROOT))
    docs = dp.read_docs()
    assert isinstance(docs, list)
    # Should find at least README if present
    if docs:
        doc = docs[0]
        assert "filename" in doc
        assert "content" in doc

def test_doc_parser_empty_dir():
    """DocumentationParser on empty dir should return empty list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dp = DocumentationParser(tmpdir)
        docs = dp.read_docs()
        assert isinstance(docs, list)
        assert len(docs) == 0

# ===== Comparator Tests =====

def test_comparator_check_consistency_finds_missing():
    """Comparator should identify code without docs."""
    code_elements = [
        {"name": "func_a", "type": "function", "file": "a.py", "line": 1, "doc": "Has doc"},
        {"name": "func_b", "type": "function", "file": "a.py", "line": 5, "doc": None},
    ]
    docs = [{"filename": "README.md", "content": "# Project"}]
    
    comp = Comparator(code_elements, docs)
    missing = comp.check_consistency()
    
    assert isinstance(missing, list)
    # func_b has no doc, should be in missing
    assert any(m["name"] == "func_b" for m in missing)

def test_comparator_returns_list():
    """Comparator.check_consistency always returns a list."""
    code_elements = [
        {"name": "func_a", "type": "function", "file": "a.py", "line": 1, "doc": "Has doc"},
    ]
    docs = [{"filename": "README.md", "content": "# Project"}]
    
    comp = Comparator(code_elements, docs)
    missing = comp.check_consistency()
    
    assert isinstance(missing, list)

def test_comparator_empty_code():
    """Comparator with no code elements should return empty list."""
    comp = Comparator([], [])
    missing = comp.check_consistency()
    assert isinstance(missing, list)
    assert len(missing) == 0

# ===== TextSuggester Tests =====

def test_suggest_text_improvements_fallback():
    """suggest_text_improvements should return dict or str fallback."""
    result = suggest_text_improvements("Example doc text")
    assert result is not None
    # Could be dict (fallback) or str (LLM)
    assert isinstance(result, (dict, str))

def test_suggest_text_improvements_empty():
    """suggest_text_improvements should handle empty input."""
    result = suggest_text_improvements("")
    assert result is not None

# ===== VisualCreator Tests =====

def test_create_visual_returns_path():
    """create_visual should return a file path string."""
    result = create_visual("Test Summary")
    assert isinstance(result, str)
    # Should be a non-empty path
    assert len(result) > 0

def test_create_visual_empty_summary():
    """create_visual should handle empty summary gracefully."""
    result = create_visual("")
    assert isinstance(result, str)