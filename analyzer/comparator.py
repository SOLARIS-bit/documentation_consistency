from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Comparator:
    """
    Compare les éléments de code avec la documentation.
    Filtre les tests et les méthodes privées pour un score réaliste.
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
        # On regroupe tout le texte de la doc en minuscule
        all_doc_text = " ".join(d.get("content", "") for d in docs).lower()

        for element in code_elements:
            full_name = element.get("name", "").lower()
            short_name = full_name.split('.')[-1]
            
            # --- FILTRES DE BRUIT ---
            # On ignore les tests, les méthodes privées et les fichiers de build
            if any(x in full_name for x in ["test_", "tests.", "conftest", "setup"]):
                continue
            if short_name.startswith("_") and short_name != "__init__":
                continue
            
            # --- FILTRES POUR LIBRAIRIES ---
            # On ignore les composants internes courants des librairies
            internal_patterns = [
                "adapter", "auth", "cookie", "mock", "mixin", "error", "warning", 
                "hook", "encoding", "utils", "helpers", "internal", "private"
            ]
            if any(pattern in full_name.lower() for pattern in internal_patterns):
                continue
            
            # --- FILTRES POUR FONCTIONS UTILITAIRES ---
            # On ignore les fonctions utilitaires communes
            utility_prefixes = ["parse_", "get_", "is_", "check_", "to_", "from_", "set_", "merge_", "default_"]
            if any(short_name.startswith(prefix) for prefix in utility_prefixes):
                continue

            # --- 1. Vérification de la Version ---
            if element.get("type") == "version":
                version_val = element.get("value")
                if version_val is not None and version_val not in all_doc_text:
                    issues.append(f"VERSION_ERROR: Code version '{version_val}' not found in docs")
                continue

            # --- 2. Vérification de l'existence ---
            if short_name not in all_doc_text:
                # Catégoriser le type d'élément manquant
                element_type = element.get("type", "unknown")
                if element_type == "class":
                    issues.append(f"MISSING_DOC_CLASS: {full_name}")
                elif element_type == "method":
                    issues.append(f"MISSING_DOC_METHOD: {full_name}")
                elif element_type == "function":
                    issues.append(f"MISSING_DOC_FUNCTION: {full_name}")
                else:
                    issues.append(f"MISSING_DOC: {full_name}")
                continue

            # --- 3. Vérification des Paramètres ---
            args = element.get("args", [])
            for arg in args:
                if arg.lower() not in all_doc_text:
                    issues.append(f"INCONSISTENCY_PARAM: Parameter '{arg}' of '{short_name}' missing in docs")

        return issues

    def check_consistency(self, require_external_docs=False):
        return self.compare(self.code_elements, self.docs)