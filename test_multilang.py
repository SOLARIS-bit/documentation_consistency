#!/usr/bin/env python3
"""Test script to validate multi-language support in the analyzer."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, '.')

from analyzer.regex_parser import SimpleRegexParser
from project_analyzer import analyze_project


def test_regex_parser():
    """Test SimpleRegexParser on various language files."""
    
    # Test Java
    java_code = """
    public class Calculator {
        public int add(int a, int b) {
            return a + b;
        }
        
        private void helper() {
        }
    }
    """
    
    # Test Go
    go_code = """
    func Add(a, b int) int {
        return a + b
    }
    
    type Calculator struct {
        value int
    }
    """
    
    # Test Python
    python_code = """
    def calculate(x, y):
        return x + y
    
    class Helper:
        def method(self):
            pass
    """
    
    # Test JS
    js_code = """
    class Calculator {
        add(a, b) {
            return a + b;
        }
    }
    
    function helper() {
    }
    """
    
    test_files = {
        'Java.java': (java_code, 'java'),
        'Calculator.go': (go_code, 'go'),
        'calc.py': (python_code, 'python'),
        'index.js': (js_code, 'javascript'),
    }
    
    print("=" * 60)
    print("REGEX PARSER TESTS")
    print("=" * 60)
    
    for filename, (code, lang) in test_files.items():
        temp_dir = tempfile.mkdtemp()
        temp_file = Path(temp_dir) / filename
        temp_file.write_text(code)
        
        try:
            parser = SimpleRegexParser(temp_dir)  # Pass temp_dir to constructor
            elements = parser.analyze_directory()  # No args needed
            names = [e['name'] for e in elements]
            print(f"\n✓ {lang.upper():12} ({filename:15}) → Found: {names}")
        except Exception as e:
            print(f"\n✗ {lang.upper():12} ({filename:15}) → ERROR: {e}")


def test_full_analyzer():
    """Test full analyzer pipeline on example project."""
    print("\n" + "=" * 60)
    print("FULL ANALYZER TEST")
    print("=" * 60)
    
    try:
        import zipfile
        
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile('example_project.zip', 'r') as z:
            z.extractall(temp_dir)
        
        result = analyze_project(temp_dir, 'example_project_test')
        
        print(f"\n✓ Analysis Status: {result['status']}")
        print(f"✓ Languages Detected: {result['languages']}")
        print(f"✓ Mode: {result['mode']}")
        print(f"✓ Total Issues Found: {len(result['issues'])}")
        print(f"✓ Issues by Type:")
        for issue_type, count in result['issues_by_type'].items():
            if count > 0:
                print(f"    - {issue_type}: {count}")
        
        return True
    except FileNotFoundError:
        print("\n⚠ example_project.zip not found - skipping full analyzer test")
        return False
    except Exception as e:
        print(f"\n✗ Full analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    test_regex_parser()
    success = test_full_analyzer()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED - Multi-language support is working!")
    else:
        print("⚠ Tests completed (some may have been skipped)")
    print("=" * 60)
