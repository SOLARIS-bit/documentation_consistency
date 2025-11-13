from analyzer.code_parser import CodeParser
from analyzer.doc_parser import DocumentationParser
from analyzer.comparator import Comparator
import json

def run_test():
    project_dir = "example_project"
    # Parse code
    cp = CodeParser(project_dir)
    code_elements = cp.analyze_directory()
    print("=== Code elements extracted ===")
    print(json.dumps(code_elements, indent=2, ensure_ascii=False))

    # Parse docs
    dp = DocumentationParser(project_dir)
    docs = dp.read_docs()
    print("\n=== Documentation files ===")
    for d in docs:
        print(f"- {d['filename']}: {len(d['content'])} chars")

    # Compare
    comp = Comparator(code_elements, docs)
    missing = comp.check_consistency()
    print("\n=== Missing in docs ===")
    if missing:
        for m in missing:
            print(f"- {m['type']} {m['name']} (docstring: {bool(m.get('doc'))})")
    else:
        print("Aucun élément manquant détecté.")

if __name__ == '__main__':
    run_test()
