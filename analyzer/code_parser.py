import ast
import os

class CodeParser:
    def __init__(self, directory):
        self.directory = directory

    def parse_file(self, filepath):
        """Analyse un fichier Python et extrait les fonctions et classes."""
        with open(filepath, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read())

        elements = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                elements.append({
                    "type": "function",
                    "name": node.name,
                    "doc": ast.get_docstring(node)
                })
            elif isinstance(node, ast.ClassDef):
                elements.append({
                    "type": "class",
                    "name": node.name,
                    "doc": ast.get_docstring(node)
                })
        return elements

    def analyze_directory(self):
        """Analyse tous les fichiers Python d’un dossier."""
        all_elements = []
        for root, _, files in os.walk(self.directory):
            for f in files:
                if f.endswith(".py"):
                    filepath = os.path.join(root, f)
                    all_elements.extend(self.parse_file(filepath))
        return all_elements


if __name__ == "__main__":
    parser = CodeParser("example_project")  # dossier à analyser
    results = parser.analyze_directory()
    for r in results:
        print(r)
