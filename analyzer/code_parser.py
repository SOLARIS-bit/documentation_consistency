import os
import ast
from typing import Any, Dict, List


class CodeParser:
    """
    Parse Python files in a directory and extract top-level functions, async functions and classes
    with their docstrings and location. This implementation has no external dependencies and
    is safe to import in test environments where optional packages (e.g. langchain) are missing.
    """

    def __init__(self, project_dir: str):
        self.project_dir = project_dir or "."

    def analyze_file(self, filepath: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception:
            return results

        try:
            node = ast.parse(source, filename=filepath)
        except SyntaxError:
            return results

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                results.append(
                    {
                        "name": child.name,
                        "type": "function",
                        "file": os.path.relpath(filepath, self.project_dir),
                        "line": getattr(child, "lineno", None),
                        "doc": ast.get_docstring(child),
                    }
                )
            elif isinstance(child, ast.ClassDef):
                # Class docstring
                results.append(
                    {
                        "name": child.name,
                        "type": "class",
                        "file": os.path.relpath(filepath, self.project_dir),
                        "line": getattr(child, "lineno", None),
                        "doc": ast.get_docstring(child),
                    }
                )
                # Methods inside class
                for sub in child.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        results.append(
                            {
                                "name": f"{child.name}.{sub.name}",
                                "type": "method",
                                "file": os.path.relpath(filepath, self.project_dir),
                                "line": getattr(sub, "lineno", None),
                                "doc": ast.get_docstring(sub),
                            }
                        )
        return results

    def analyze_directory(self) -> List[Dict[str, Any]]:
        elements: List[Dict[str, Any]] = []
        if not os.path.isdir(self.project_dir):
            # If the directory doesn't exist, try current directory
            base_dir = "."
        else:
            base_dir = self.project_dir

        for root, _, files in os.walk(base_dir):
            # Skip virtualenv and common binary dirs
            if any(part.startswith(".venv") or part == "__pycache__" for part in root.split(os.sep)):
                continue
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                path = os.path.join(root, fname)
                elements.extend(self.analyze_file(path))

        # Ensure deterministic ordering for tests
        elements.sort(key=lambda e: (e.get("file") or "", e.get("line") or 0, e.get("name") or ""))
        return elements