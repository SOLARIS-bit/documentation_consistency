from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from analyzer.code_parser import CodeParser
from analyzer.doc_parser import DocumentationParser
from analyzer.comparator import Comparator

# Optional LLM imports (always define names)
try:
    from langchain_openai import ChatOpenAI  # type: ignore
    from langchain_core.prompts import PromptTemplate  # type: ignore
    from langchain_core.messages import BaseMessage  # type: ignore
    LLM_AVAILABLE = True
except Exception:
    ChatOpenAI = None  # type: ignore
    PromptTemplate = None  # type: ignore
    BaseMessage = None  # type: ignore
    LLM_AVAILABLE = False


def analyze_project(project_path: str) -> Dict[str, Any]:
    """
    Full project analyzer: returns dict with status, issues, samples, mode, optional llm result.
    """
    project_path_str: str = str(project_path)
    project_path_obj: Path = Path(project_path_str)

    # Get Python files
    py_files: List[Path] = list(project_path_obj.rglob("*.py"))  # type: ignore
    checked_samples: int = 0
    issues: List[str] = []

    parser = CodeParser(project_dir=project_path_str)
    doc_parser = DocumentationParser(directory=project_path_str)
    comparator = Comparator()

    for file_path in py_files:
        file_str: str = str(file_path)

        try:
            code_info = parser.analyze_file(file_str)
            doc_info = doc_parser.parse_file(file_str)

            comparison = comparator.compare(code_info, doc_info)

            if comparison:
                issues.extend(comparison)

            checked_samples += 1

        except Exception:
            continue

    result: Dict[str, Any] = {
        "status": "ok" if checked_samples > 0 else "fallback",
        "issues": issues,
        "checked_samples": checked_samples,
        "mode": "deterministic",
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