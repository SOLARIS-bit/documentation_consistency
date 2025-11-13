import os
import markdown

class DocumentationParser:
    def __init__(self, directory):
        self.directory = directory

    def read_docs(self):
        """Lit les fichiers Markdown et retourne leur contenu brut."""
        docs = []
        for root, _, files in os.walk(self.directory):
            for f in files:
                if f.endswith(".md") or f.endswith(".txt"):
                    filepath = os.path.join(root, f)
                    with open(filepath, "r", encoding="utf-8") as file:
                        docs.append({
                            "filename": f,
                            "content": file.read()
                        })
        return docs


if __name__ == "__main__":
    parser = DocumentationParser("example_project")
    docs = parser.read_docs()
    for d in docs:
        print(f"\n📄 {d['filename']}:\n{d['content'][:200]}...")
