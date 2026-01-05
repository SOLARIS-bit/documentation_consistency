import os
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

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
            logger.debug(f"Skipping non-documentation file: {filepath}")
            return []

        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to read documentation file {filepath}: {str(e)}")
            return []

        logger.debug(f"Parsed documentation file: {filepath}")
        return [{
            "file": str(filepath.relative_to(self.directory)),
            "content": content,
        }]

    def parse_directory(self) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        logger.info(f"Starting documentation scan: {self.directory}")

        if not self.directory.is_dir():
            logger.warning(f"Documentation directory not found: {self.directory}")
            return docs

        for root, _, files in os.walk(str(self.directory)):
            for fname in files:
                if fname.endswith(".md") or fname.endswith(".txt"):
                    full_path = Path(root) / fname
                    docs.extend(self.parse_file(full_path))
        
        logger.info(f"Documentation scan complete: found {len(docs)} files")
        return docs

    # Optional backward compatibility
    def read_docs(self) -> List[Dict[str, Any]]:
        return self.parse_directory()