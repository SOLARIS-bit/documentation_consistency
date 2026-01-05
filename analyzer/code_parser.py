import os
import ast
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

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
        # Skip test-related files
        if 'test' in str(filepath).lower() or 'spec' in str(filepath).lower() or 'conftest' in str(filepath).lower():
            logger.debug(f"Skipping test file: {filepath}")
            return results
        try:
            source = filepath.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to read file {filepath}: {str(e)}")
            return results

        try:
            node = ast.parse(source, filename=str(filepath))
        except SyntaxError as e:
            logger.warning(f"Syntax error in {filepath}: {str(e)}")
            return results

        for child in ast.iter_child_nodes(node):
            # --- NOUVEAU : Détection de la version du projet ---
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and target.id == "__version__":
                        if isinstance(child.value, ast.Constant): # Python 3.8+
                            results.append({
                                "name": "__version__",
                                "type": "version",
                                "value": str(child.value.value),
                                "file": str(filepath.relative_to(self.project_dir))
                            })
            # --- Fonctions et Méthodes ---
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not child.name.startswith('_'):
                    results.append(self._extract_function_info(child, filepath))
                
            elif isinstance(child, ast.ClassDef):
                if not child.name.startswith('_'):
                    results.append({
                        "name": child.name,
                        "type": "class",
                        "file": str(filepath.relative_to(self.project_dir)),
                        "line": getattr(child, "lineno", None),
                        "doc": ast.get_docstring(child),
                    })
                    for sub in child.body:
                        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not sub.name.startswith('_'):
                                results.append(self._extract_function_info(sub, filepath, prefix=child.name))
        return results
    def _extract_function_info(self, node, filepath, prefix=None):
        """Helper pour extraire les arguments d'une fonction"""
        name = f"{prefix}.{node.name}" if prefix else node.name
        # On extrait les noms des arguments (en ignorant 'self' et 'cls')
        args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
        
        return {
            "name": name,
            "type": "method" if prefix else "function",
            "file": str(filepath.relative_to(self.project_dir)),
            "line": getattr(node, "lineno", None),
            "doc": ast.get_docstring(node),
            "args": args # <--- CRUCIAL pour la détection d'incohérences
        } 

    def analyze_directory(self) -> List[Dict[str, Any]]:
        elements: List[Dict[str, Any]] = []
        logger.info(f"Starting directory analysis: {self.project_dir}")
        
        # Dossiers à bannir (en minuscules pour la comparaison)
        BLACKLIST_DIRS = {'tests', 'testing', 'docs', 'scripts', 'examples', 'venv', '.git', 'test', 'spec', 'conftest'}

        for root, dirs, files in os.walk(self.project_dir):
            # 1. Sécurité au niveau des dossiers
            # On modifie 'dirs' pour que os.walk ne descende pas dedans
            dirs[:] = [d for d in dirs if d.lower() not in BLACKLIST_DIRS]

            for fname in files:
                # 2. Sécurité au niveau des fichiers
                if not fname.endswith(".py"):
                    continue
                
                # On ignore tout fichier qui contient "test" dans son nom
                if "test" in fname.lower():
                    continue
                
                name = fname
                # 4. On ignore les tests
                if name.startswith("test_") or name.startswith("Test"):
                    continue

                # 5. On ignore les méthodes privées (souvent de l'implémentation interne)
                if name.startswith("_") and not name.startswith("__"):
                    continue

                # 6. Cas spécial pour __init__ (souvent documenté dans la classe)
                if name == "__init__":
                    continue

                path = Path(root) / fname
                try:
                    elements.extend(self.analyze_file(path))
                except Exception as e:
                    print(f"Error parsing {fname}: {e}")

        return elements