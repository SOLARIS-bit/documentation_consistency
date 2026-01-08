from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

from analyzer.code_parser import CodeParser
from analyzer.doc_parser import DocumentationParser
from analyzer.comparator import Comparator

logger = logging.getLogger(__name__)

# Optional LLM imports (always define names)
try:
    from langchain_openai import ChatOpenAI  # type: ignore
    from langchain_core.prompts import PromptTemplate  # type: ignore
    from langchain_core.messages import BaseMessage  # type: ignore
    LLM_AVAILABLE = True
    logger.info("LLM support enabled (LangChain + OpenAI available)")
except Exception as e:
    ChatOpenAI = None  # type: ignore
    PromptTemplate = None  # type: ignore
    BaseMessage = None  # type: ignore
    LLM_AVAILABLE = False
    logger.debug(f"LLM support disabled: {str(e)}")


def analyze_project(project_path: str) -> Dict[str, Any]:
    """
    Full project analyzer: returns dict with status, issues, samples, mode, optional llm result.
    """
    project_path_str: str = str(project_path)
    project_path_obj: Path = Path(project_path_str)
    
    logger.info(f"Starting project analysis: {project_path_str}")

    # Get Python files
    py_files: List[Path] = list(project_path_obj.rglob("*.py"))  # type: ignore
    checked_samples: int = 0
    
    logger.debug(f"Found {len(py_files)} Python files in project")
    issues: List[str] = []

    parser = CodeParser(project_dir=project_path_str)
    doc_parser = DocumentationParser(directory=project_path_str)
    comparator = Comparator()

    # Stats counters
    total_elements: int = 0
    classes_count: int = 0
    functions_count: int = 0
    methods_count: int = 0

    # CRUCIAL : On lit TOUTE la doc (README, etc.) une seule fois ici
    all_docs = doc_parser.parse_directory() 

    for file_path in py_files:
        file_str: str = str(file_path)

        try:
            # On extrait les fonctions/classes du fichier Python
            code_info = parser.analyze_file(file_str)

            # Update stats counters
            for el in code_info:
                total_elements += 1
                t = el.get("type")
                if t == "class":
                    classes_count += 1
                elif t == "function":
                    functions_count += 1
                elif t == "method":
                    methods_count += 1
            
            # AU LIEU DE : doc_info = doc_parser.parse_file(file_str)
            # ON UTILISE : all_docs qu'on a chargé plus haut
            comparison = comparator.compare(code_info, all_docs)

            if comparison:
                issues.extend(comparison)

            checked_samples += 1
        except Exception:
            continue

    # Issues by type breakdown
    missing_classes = sum(1 for i in issues if "MISSING_DOC_CLASS" in i)
    missing_methods = sum(1 for i in issues if "MISSING_DOC_METHOD" in i)
    missing_functions = sum(1 for i in issues if "MISSING_DOC_FUNCTION" in i)
    param_issues = sum(1 for i in issues if "INCONSISTENCY_PARAM" in i)

    result: Dict[str, Any] = {
        "status": "ok" if checked_samples > 0 else "fallback",
        "issues": issues,
        "checked_samples": checked_samples,
        "mode": "deterministic",
        "stats": {
            "total_elements": total_elements,
            "classes": classes_count,
            "functions": functions_count,
            "methods": methods_count,
        },
        "issues_by_type": {
            "MISSING_DOC_CLASS": missing_classes,
            "MISSING_DOC_METHOD": missing_methods,
            "MISSING_DOC_FUNCTION": missing_functions,
            "INCONSISTENCY_PARAM": param_issues,
        }
    }

    # ------------------------
    # LLM AUGMENTATION
    # ------------------------
    if LLM_AVAILABLE and ChatOpenAI and PromptTemplate and len(issues) > 0:

        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)  # type: ignore

            prompt = PromptTemplate.from_template(  # type: ignore
                """
Tu es un assistant expert.
Voici les problèmes détectés :
{issues}

Donne une analyse concise et des suggestions d'amélioration.
"""
            )

            llm_output = llm.invoke(prompt.format(issues="\n".join(issues)))  # type: ignore
            llm_text = normalize_llm_output(llm_output)

            result["mode"] = "llm_augmented"
            result["llm_analysis"] = llm_text

        except Exception:
            pass

    return result


def normalize_llm_output(response: Any) -> str:
    """Ensure the LLM output is always a pure string."""
    if BaseMessage and isinstance(response, BaseMessage):  # type: ignore
        return str(response.content)

    if isinstance(response, str):
        return response

    if isinstance(response, list):
        return "\n".join(str(item) for item in response)

    return str(response)