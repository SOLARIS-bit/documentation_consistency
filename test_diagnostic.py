#!/usr/bin/env python3
"""
Diagnostic script to test code analysis on example_project
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from analyzer.code_parser import CodeParser
from analyzer.tree_sitter_parser import TreeSitterParser
from analyzer.doc_parser import DocumentationParser
from project_analyzer import analyze_project

def test_example_project():
    """Test analysis of the example_project directory"""
    example_project = Path(__file__).parent / "example_project"
    
    print(f"\n{'='*60}")
    print(f"Testing analysis of: {example_project}")
    print(f"{'='*60}\n")
    
    if not example_project.exists():
        print(f"❌ Error: {example_project} does not exist")
        return
    
    # List directory contents
    print("📁 Directory contents:")
    for item in example_project.iterdir():
        print(f"   {item.name}")
    
    # Test CodeParser
    print(f"\n{'─'*60}")
    print("🔵 Testing CodeParser...")
    print(f"{'─'*60}")
    py_parser = CodeParser(project_dir=str(example_project))
    py_elements = py_parser.analyze_directory()
    print(f"\n✅ CodeParser found {len(py_elements)} elements:")
    for el in py_elements:
        print(f"   - {el['type']:10} | {el['name']:30} | {el['file']}")
    
    # Test TreeSitterParser
    print(f"\n{'─'*60}")
    print("🟢 Testing TreeSitterParser...")
    print(f"{'─'*60}")
    ts_parser = TreeSitterParser(project_dir=str(example_project))
    ts_elements = ts_parser.analyze_directory()
    print(f"\n✅ TreeSitterParser found {len(ts_elements)} elements:")
    for el in ts_elements:
        print(f"   - {el['type']:10} | {el['name']:30} | {el.get('language', 'unknown'):10} | {el['file']}")
    
    # Test DocumentationParser
    print(f"\n{'─'*60}")
    print("🟡 Testing DocumentationParser...")
    print(f"{'─'*60}")
    doc_parser = DocumentationParser(directory=str(example_project))
    docs = doc_parser.parse_directory()
    print(f"\n✅ DocumentationParser found {len(docs)} documentation sections:")
    for doc in docs[:5]:  # Show first 5
        content_preview = doc.get('content', '')[:100].replace('\n', ' ')
        print(f"   - {doc.get('file', 'unknown'):30} | {content_preview}...")
    
    # Test full analyze_project
    print(f"\n{'─'*60}")
    print("🔴 Testing full analyze_project()...")
    print(f"{'─'*60}\n")
    result = analyze_project(str(example_project), project_name="ExampleProject")
    
    print(f"✅ Analysis result:")
    print(f"   Status: {result.get('status')}")
    print(f"   Mode: {result.get('mode')}")
    print(f"   Languages: {result.get('languages', [])}")
    print(f"   Files analyzed: {result.get('checked_samples')}")
    print(f"   Total issues: {len(result.get('issues', []))}")
    print(f"   Stats: {result.get('stats')}")
    
    if result.get('issues'):
        print(f"\n   Issues found:")
        for issue in result['issues'][:5]:
            print(f"      - {issue}")

if __name__ == "__main__":
    test_example_project()
