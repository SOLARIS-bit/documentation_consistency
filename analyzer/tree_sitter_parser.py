import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from tree_sitter import Language, Parser
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False
    logger.warning("tree-sitter not installed. Install with: pip install tree-sitter")

# Try to import pre-built language libraries
HAS_TREE_SITTER_LANGUAGES = False
try:
    import tree_sitter_languages as tsl
    HAS_TREE_SITTER_LANGUAGES = True
    logger.debug("tree-sitter-languages package available")
except ImportError:
    logger.debug("tree-sitter-languages package not found")


class TreeSitterParser:
    """
    Multi-language code parser using tree-sitter.
    Supports: Python, Java, C, C++, Go, JavaScript, TypeScript, Rust, C#, etc.
    """

    # Language extension mapping
    LANGUAGE_EXTENSIONS = {
        'python': ['.py'],
        'java': ['.java'],
        'c': ['.c', '.h'],
        'cpp': ['.cc', '.cpp', '.cxx', '.h', '.hpp'],
        'go': ['.go'],
        'javascript': ['.js', '.jsx'],
        'typescript': ['.ts', '.tsx'],
        'rust': ['.rs'],
        'c_sharp': ['.cs'],
        'ruby': ['.rb'],
        'php': ['.php'],
    }

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir: Path = Path(project_dir)
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        self._initialize_parsers()

    def _initialize_parsers(self):
        """Initialize tree-sitter parsers for all supported languages."""
        if not HAS_TREE_SITTER:
            logger.warning("tree-sitter not available; will use fallback Python parser")
            return

        supported_langs = ['python', 'java', 'c', 'cpp', 'go', 'javascript', 'typescript', 'rust', 'c_sharp']
        initialized_count = 0
        
        for lang in supported_langs:
            try:
                language = None
                
                # Try tree-sitter-languages package first (easier to use)
                if HAS_TREE_SITTER_LANGUAGES:
                    try:
                        language = tsl.get_language(lang)
                        logger.debug(f"Loaded {lang} from tree-sitter-languages")
                    except Exception as e:
                        logger.debug(f"Could not load {lang} from tree-sitter-languages: {e}")
                
                # Fallback to manual library loading
                if language is None:
                    lib_path = self._get_language_lib_path(lang)
                    if lib_path and os.path.exists(lib_path):
                        language = Language(lib_path, lang)
                        logger.debug(f"Loaded {lang} from manual library path: {lib_path}")
                
                # Register the language
                if language is not None:
                    self.languages[lang] = language
                    parser = Parser()
                    parser.set_language(language)
                    self.parsers[lang] = parser
                    initialized_count += 1
                    logger.debug(f"Initialized parser for {lang}")
                else:
                    logger.debug(f"Language library not found for {lang}")
            except Exception as e:
                logger.debug(f"Could not initialize {lang} parser: {e}")
        
        if initialized_count == 0:
            logger.warning(f"No tree-sitter language libraries found. Install with: pip install tree-sitter-languages")

    def _get_language_lib_path(self, lang: str) -> Optional[str]:
        """Get the path to the tree-sitter language library."""
        # Common installation paths
        possible_paths = [
            f"~/.local/lib/libtree_sitter_{lang}.so",
            f"/usr/lib/libtree_sitter_{lang}.so",
            f"/usr/local/lib/libtree_sitter_{lang}.so",
            f"/opt/libtree_sitter_{lang}.so",
        ]
        
        for path in possible_paths:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                return expanded
        return None

    def get_language_for_file(self, filepath: Path) -> Optional[str]:
        """Determine the language based on file extension."""
        ext = filepath.suffix.lower()
        for lang, exts in self.LANGUAGE_EXTENSIONS.items():
            if ext in exts:
                return lang
        return None

    def analyze_file(self, filepath: str | Path) -> List[Dict[str, Any]]:
        """
        Parse a file and extract functions, classes, and methods.
        Returns a list of code elements with their metadata.
        """
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
            source_code = filepath.read_bytes()
        except Exception as e:
            logger.warning(f"Failed to read file {filepath}: {e}")
            return []

        # Use tree-sitter if available, otherwise fallback
        if language in self.parsers:
            return self._parse_with_tree_sitter(source_code, filepath, language)
        else:
            logger.debug(f"No parser available for {language}, skipping {filepath}")
            return []

    def _parse_with_tree_sitter(self, source_code: bytes, filepath: Path, language: str) -> List[Dict[str, Any]]:
        """Parse code using tree-sitter and extract elements."""
        results: List[Dict[str, Any]] = []
        
        try:
            parser = self.parsers[language]
            tree = parser.parse(source_code)
            root = tree.root_node
            
            # Extract elements based on language
            if language == 'python':
                results = self._extract_python_elements(root, source_code, filepath, language)
            elif language == 'java':
                results = self._extract_java_elements(root, source_code, filepath, language)
            elif language in ['c', 'cpp']:
                results = self._extract_c_elements(root, source_code, filepath, language)
            elif language == 'go':
                results = self._extract_go_elements(root, source_code, filepath, language)
            elif language in ['javascript', 'typescript']:
                results = self._extract_js_elements(root, source_code, filepath, language)
            elif language == 'rust':
                results = self._extract_rust_elements(root, source_code, filepath, language)
            elif language == 'c_sharp':
                results = self._extract_csharp_elements(root, source_code, filepath, language)
            
        except Exception as e:
            logger.warning(f"Error parsing {filepath} with tree-sitter: {e}")

        return results

    def _get_text(self, node, source_code: bytes) -> str:
        """Extract text from a node."""
        return source_code[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')

    def _get_docstring(self, node, source_code: bytes) -> Optional[str]:
        """Extract docstring/comment from a node."""
        # Look for preceding comment/docstring
        prev_node = node.prev_sibling
        if prev_node and prev_node.type in ['comment', 'block_comment', 'line_comment', 'string']:
            return self._get_text(prev_node, source_code).strip()
        return None

    def _extract_python_elements(self, node, source_code: bytes, filepath: Path, language: str) -> List[Dict[str, Any]]:
        """Extract Python functions and classes."""
        results: List[Dict[str, Any]] = []
        
        def traverse(node, class_prefix: str = ""):
            if node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = self._get_text(name_node, source_code)
                    if not func_name.startswith('_'):
                        full_name = f"{class_prefix}.{func_name}" if class_prefix else func_name
                        results.append({
                            "name": full_name,
                            "type": "method" if class_prefix else "function",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
            elif node.type == 'class_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    class_name = self._get_text(name_node, source_code)
                    if not class_name.startswith('_'):
                        results.append({
                            "name": class_name,
                            "type": "class",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
                        # Traverse class methods
                        for child in node.children:
                            traverse(child, class_prefix=class_name)
                        return  # Don't continue traversing children
            
            # Recurse
            for child in node.children:
                traverse(child, class_prefix)
        
        traverse(node)
        return results

    def _extract_java_elements(self, node, source_code: bytes, filepath: Path, language: str) -> List[Dict[str, Any]]:
        """Extract Java classes and methods."""
        results: List[Dict[str, Any]] = []
        
        def traverse(node, class_prefix: str = ""):
            if node.type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    method_name = self._get_text(name_node, source_code)
                    if not method_name.startswith('_'):
                        full_name = f"{class_prefix}.{method_name}" if class_prefix else method_name
                        results.append({
                            "name": full_name,
                            "type": "method" if class_prefix else "function",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
            elif node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    class_name = self._get_text(name_node, source_code)
                    results.append({
                        "name": class_name,
                        "type": "class",
                        "file": str(filepath.relative_to(self.project_dir)),
                        "line": node.start_point[0] + 1,
                        "language": language,
                        "doc": self._get_docstring(node, source_code),
                    })
                    # Traverse class methods
                    for child in node.children:
                        traverse(child, class_prefix=class_name)
                    return
            
            for child in node.children:
                traverse(child, class_prefix)
        
        traverse(node)
        return results

    def _extract_c_elements(self, node, source_code: bytes, filepath: Path, language: str) -> List[Dict[str, Any]]:
        """Extract C/C++ functions."""
        results: List[Dict[str, Any]] = []
        
        def traverse(node):
            if node.type == 'function_definition':
                declarator = node.child_by_field_name('declarator')
                if declarator:
                    func_name = self._extract_identifier(declarator, source_code)
                    if func_name and not func_name.startswith('_'):
                        results.append({
                            "name": func_name,
                            "type": "function",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return results

    def _extract_go_elements(self, node, source_code: bytes, filepath: Path, language: str) -> List[Dict[str, Any]]:
        """Extract Go functions and methods."""
        results: List[Dict[str, Any]] = []
        
        def traverse(node):
            if node.type == 'function_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = self._get_text(name_node, source_code)
                    if not func_name.startswith('_'):
                        results.append({
                            "name": func_name,
                            "type": "function",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
            elif node.type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    method_name = self._get_text(name_node, source_code)
                    if not method_name.startswith('_'):
                        results.append({
                            "name": method_name,
                            "type": "method",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
        return results

    def _extract_js_elements(self, node, source_code: bytes, filepath: Path, language: str) -> List[Dict[str, Any]]:
        """Extract JavaScript/TypeScript functions and classes."""
        results: List[Dict[str, Any]] = []
        
        def traverse(node, class_prefix: str = ""):
            if node.type in ['function_declaration', 'arrow_function']:
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = self._get_text(name_node, source_code)
                    if not func_name.startswith('_'):
                        full_name = f"{class_prefix}.{func_name}" if class_prefix else func_name
                        results.append({
                            "name": full_name,
                            "type": "method" if class_prefix else "function",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
            elif node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    class_name = self._get_text(name_node, source_code)
                    results.append({
                        "name": class_name,
                        "type": "class",
                        "file": str(filepath.relative_to(self.project_dir)),
                        "line": node.start_point[0] + 1,
                        "language": language,
                        "doc": self._get_docstring(node, source_code),
                    })
                    for child in node.children:
                        traverse(child, class_prefix=class_name)
                    return
            
            for child in node.children:
                traverse(child, class_prefix)
        
        traverse(node)
        return results

    def _extract_rust_elements(self, node, source_code: bytes, filepath: Path, language: str) -> List[Dict[str, Any]]:
        """Extract Rust functions and structs."""
        results: List[Dict[str, Any]] = []
        
        def traverse(node, struct_prefix: str = ""):
            if node.type == 'function_item':
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = self._get_text(name_node, source_code)
                    if not func_name.startswith('_'):
                        full_name = f"{struct_prefix}.{func_name}" if struct_prefix else func_name
                        results.append({
                            "name": full_name,
                            "type": "method" if struct_prefix else "function",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
            elif node.type == 'struct_item':
                name_node = node.child_by_field_name('name')
                if name_node:
                    struct_name = self._get_text(name_node, source_code)
                    results.append({
                        "name": struct_name,
                        "type": "class",
                        "file": str(filepath.relative_to(self.project_dir)),
                        "line": node.start_point[0] + 1,
                        "language": language,
                        "doc": self._get_docstring(node, source_code),
                    })
            
            for child in node.children:
                traverse(child, struct_prefix)
        
        traverse(node)
        return results

    def _extract_csharp_elements(self, node, source_code: bytes, filepath: Path, language: str) -> List[Dict[str, Any]]:
        """Extract C# classes and methods."""
        results: List[Dict[str, Any]] = []
        
        def traverse(node, class_prefix: str = ""):
            if node.type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    method_name = self._get_text(name_node, source_code)
                    if not method_name.startswith('_'):
                        full_name = f"{class_prefix}.{method_name}" if class_prefix else method_name
                        results.append({
                            "name": full_name,
                            "type": "method" if class_prefix else "function",
                            "file": str(filepath.relative_to(self.project_dir)),
                            "line": node.start_point[0] + 1,
                            "language": language,
                            "doc": self._get_docstring(node, source_code),
                        })
            elif node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    class_name = self._get_text(name_node, source_code)
                    results.append({
                        "name": class_name,
                        "type": "class",
                        "file": str(filepath.relative_to(self.project_dir)),
                        "line": node.start_point[0] + 1,
                        "language": language,
                        "doc": self._get_docstring(node, source_code),
                    })
                    for child in node.children:
                        traverse(child, class_prefix=class_name)
                    return
            
            for child in node.children:
                traverse(child, class_prefix)
        
        traverse(node)
        return results

    def _extract_identifier(self, node, source_code: bytes) -> Optional[str]:
        """Extract identifier from a declarator node."""
        if node.type == 'identifier':
            return self._get_text(node, source_code)
        for child in node.children:
            result = self._extract_identifier(child, source_code)
            if result:
                return result
        return None

    def analyze_directory(self) -> List[Dict[str, Any]]:
        """Analyze all code files in the project directory."""
        elements: List[Dict[str, Any]] = []
        logger.info(f"Starting multi-language analysis: {self.project_dir}")
        
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
                        elements.extend(self.analyze_file(path))
                    except Exception as e:
                        logger.error(f"Error parsing {path}: {e}")

        return elements
