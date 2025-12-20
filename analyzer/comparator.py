from typing import List, Dict, Any, Optional


class Comparator:
    """
    Compare code elements with documentation elements.
    Returns list of missing documentation items.
    """

    def __init__(
        self, 
        code_elements: Optional[List[Dict[str, Any]]] = None, 
        docs: Optional[List[Dict[str, Any]]] = None
    ):
        self.code_elements: List[Dict[str, Any]] = code_elements or []
        self.docs: List[Dict[str, Any]] = docs or []

    def compare(self, code_elements: List[Dict[str, Any]], docs: List[Dict[str, Any]]) -> List[str]:
        issues: List[str] = []
        all_doc_text = " ".join(d.get("content", "") for d in docs).lower()

        for element in code_elements:
            name = element.get("name", "").lower()
            if name not in all_doc_text:
                issues.append(f"Missing documentation for: {name}")

        return issues

    # Optional backward compatibility for old tests
    def check_consistency(self) -> List[Dict[str, Any]]:
        missing: List[Dict[str, Any]] = []
        all_doc_text = " ".join(d.get("content", "") for d in self.docs).lower()

        for element in self.code_elements:
            name = element.get("name", "").lower()
            if name not in all_doc_text:
                missing.append(element)

        return missing