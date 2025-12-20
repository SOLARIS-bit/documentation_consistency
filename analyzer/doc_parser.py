import os
from pathlib import Path
from typing import List, Dict, Any


class DocumentationParser:
    """
    Parse documentation files (.md, .txt) either individually or by directory.
    Returns list of dicts with keys 'file' and 'content'.
    """

    def __init__(self, directory: str | Path = "."):
        self.directory: Path = Path(directory)

    def parse_file(self, filepath: str | Path) -> List[Dict[str, Any]]:
        filepath = Path(filepath)
        if not filepath.is_file() or filepath.suffix not in {".md", ".txt"}:
            return []

        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            return []

        return [{
            "file": str(filepath.relative_to(self.directory)),
            "content": content,
        }]

    def parse_directory(self) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []

        if not self.directory.is_dir():
            return docs

        for root, _, files in os.walk(str(self.directory)):
            for fname in files:
                if fname.endswith(".md") or fname.endswith(".txt"):
                    full_path = Path(root) / fname
                    docs.extend(self.parse_file(full_path))

        return docs

    # Optional backward compatibility
    def read_docs(self) -> List[Dict[str, Any]]:
        return self.parse_directory()