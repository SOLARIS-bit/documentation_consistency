import os
import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SimpleRegexParser:
    """
    Simple regex-based multi-language code parser.
    Works for: Java, C, Go, JavaScript, TypeScript, Rust, C#, PHP, Ruby
    """

    PATTERNS = {
        'python': {
            'function': r'^def\s+(\w+)\s*\(',
            'class': r'^class\s+(\w+)',
        },
        'java': {
            'class': r'(?:public\s+)?class\s+(\w+)',
            'method': r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\(',
        },
        'c': {
            'function': r'(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*\{',
        },
        'cpp': {
            'class': r'(?:class|struct)\s+(\w+)',
            'function': r'(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*[\{;]',
        },
        'go': {
            'function': r'func\s+(?:\([\w\s*]+\)\s+)?(\w+)\s*\(',
            'struct': r'type\s+(\w+)\s+struct',
        },
        'javascript': {
            'class': r'class\s+(\w+)',
            'function': r'(?:async\s+)?function\s+(\w+)\s*\(|const\s+(\w+)\s*=.*(?:function|\()',
        },
        'typescript': {
            'class': r'(?:export\s+)?class\s+(\w+)',
            'function': r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(|export\s+const\s+(\w+)',
        },
        'rust': {
            'function': r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(',
            'struct': r'(?:pub\s+)?struct\s+(\w+)',
        },
        'c_sharp': {
            'class': r'(?:public\s+)?class\s+(\w+)',
            'method': r'(?:public|private|protected)?\s*(?:static\s+)?(?:async\s+)?(?:\w+\s+)+(\w+)\s*\(',
        },
        'php': {
            'class': r'class\s+(\w+)',
            'function': r'function\s+(\w+)\s*\(',
        },
        'ruby': {
            'class': r'class\s+(\w+)',
            'function': r'def\s+(\w+)',
        },
    }

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir: Path = Path(project_dir)

    def get_language_for_file(self, filepath: Path) -> Optional[str]:
        """Determine the language based on file extension."""
        ext_map = {
            '.java': 'java',
            '.c': 'c',
            '.h': 'c',
            '.cc': 'cpp',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.hpp': 'cpp',
            '.go': 'go',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.rs': 'rust',
            '.cs': 'c_sharp',
            '.php': 'php',
            '.rb': 'ruby',
        }
        return ext_map.get(filepath.suffix.lower())

    def analyze_file(self, filepath: str | Path) -> List[Dict[str, Any]]:
        """Parse a file and extract functions, classes, and methods."""
        filepath = Path(filepath)

        # Skip test files
        if 'test' in str(filepath).lower() or 'spec' in str(filepath).lower():
            logger.debug(f"Skipping test file: {filepath}")
            return []

        language = self.get_language_for_file(filepath)
        if not language:
            logger.debug(f"Unsupported file type: {filepath}")
            return []

        try:
            source_code = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"Failed to read file {filepath}: {e}")
            return []

        results: List[Dict[str, Any]] = []
        patterns = self.PATTERNS.get(language, {})

        for elem_type, pattern in patterns.items():
            try:
                for match in re.finditer(pattern, source_code, re.MULTILINE):
                    name = None
                    # Handle multiple capture groups
                    for group in match.groups():
                        if group:
                            name = group
                            break

                    if name and not name.startswith('_'):
                        results.append({
                            "name": name,
                            "type": elem_type,
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": source_code[:match.start()].count('\n') + 1,
                            "language": language,
                        })
            except Exception as e:
                logger.debug(f"Regex pattern error in {language} for {elem_type}: {e}")

        return results

    def analyze_directory(self) -> List[Dict[str, Any]]:
        """Analyze all code files in the project directory."""
        elements: List[Dict[str, Any]] = []
        logger.info(f"Starting regex-based multi-language analysis: {self.project_dir}")

        BLACKLIST_DIRS = {'tests', 'testing', 'docs', 'scripts', 'examples', 'venv', '.git', 'test', 'spec', '__pycache__', 'node_modules', 'target', 'build', 'dist'}

        for root, dirs, files in os.walk(self.project_dir):
            dirs[:] = [d for d in dirs if d.lower() not in BLACKLIST_DIRS]

            for fname in files:
                # Check if file is supported
                if self.get_language_for_file(Path(fname)):
                    # Skip test files
                    if "test" in fname.lower():
                        continue

                    path = Path(root) / fname
                    try:
                        file_elements = self.analyze_file(path)
                        if file_elements:
                            logger.debug(f"Found {len(file_elements)} elements in {fname}")
                        elements.extend(file_elements)
                    except Exception as e:
                        logger.error(f"Error parsing {path}: {e}")

        logger.info(f"Regex-based analysis found {len(elements)} total elements")
        return elements
