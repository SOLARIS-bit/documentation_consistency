import os
import ast
from pathlib import Path
from typing import Any, Dict, List


class CodeParser:
    """
    Parse Python files in a directory and extract top-level functions,
    async functions, and classes with their docstrings and location.
    """

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir: Path = Path(project_dir)

    # Alias for compatibility
    def parse_file(self, filepath: str | Path) -> List[Dict[str, Any]]:
        return self.analyze_file(filepath)

    def analyze_file(self, filepath: str | Path) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        filepath = Path(filepath)
        try:
            source = filepath.read_text(encoding="utf-8")
        except Exception:
            return results

        try:
            node = ast.parse(source, filename=str(filepath))
        except SyntaxError:
            return results

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                results.append({
                    "name": child.name,
                    "type": "function",
                    "file": str(filepath.relative_to(self.project_dir)),
                    "line": getattr(child, "lineno", None),
                    "doc": ast.get_docstring(child),
                })
            elif isinstance(child, ast.ClassDef):
                results.append({
                    "name": child.name,
                    "type": "class",
                    "file": str(filepath.relative_to(self.project_dir)),
                    "line": getattr(child, "lineno", None),
                    "doc": ast.get_docstring(child),
                })
                for sub in child.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        results.append({
                            "name": f"{child.name}.{sub.name}",
                            "type": "method",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": getattr(sub, "lineno", None),
                            "doc": ast.get_docstring(sub),
                        })
        return results

    def analyze_directory(self) -> List[Dict[str, Any]]:
        elements: List[Dict[str, Any]] = []

        if not self.project_dir.is_dir():
            return elements

        for root, _, files in os.walk(str(self.project_dir)):
            if any(part.startswith(".venv") or part == "__pycache__" for part in Path(root).parts):
                continue
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                path = Path(root) / fname
                elements.extend(self.analyze_file(path))

        elements.sort(key=lambda e: (e.get("file") or "", e.get("line") or 0, e.get("name") or ""))
        return elements