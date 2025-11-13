import re

class Comparator:
    def __init__(self, code_elements, docs):
        self.code_elements = code_elements
        self.docs = docs

    def check_consistency(self):
        """Compare le code et la doc et détecte les éléments manquants."""
        missing = []
        all_doc_text = " ".join(d["content"] for d in self.docs)

        for element in self.code_elements:
            if element["name"] not in all_doc_text:
                missing.append(element)
        return missing


if __name__ == "__main__":
    from code_parser import CodeParser
    from doc_parser import DocumentationParser

    code_parser = CodeParser("example_project")
    doc_parser = DocumentationParser("example_project")

    code_data = code_parser.analyze_directory()
    doc_data = doc_parser.read_docs()

    comparator = Comparator(code_data, doc_data)
    missing = comparator.check_consistency()

    print("\n⚠️ Fonctions / classes non documentées :")
    for m in missing:
        print(f" - {m['type']} {m['name']}")
