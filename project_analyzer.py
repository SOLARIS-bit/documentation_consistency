from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

from analyzer.code_parser import CodeParser
from analyzer.regex_parser import SimpleRegexParser
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


def analyze_project(project_path: str, project_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Full project analyzer: returns dict with status, issues, samples, mode, optional llm result.
    Supports multiple languages via tree-sitter (Java, C, C++, Go, JavaScript, etc.)
    """
    project_path_str: str = str(project_path)
    project_path_obj: Path = Path(project_path_str)
    
    # Use provided project_name or extract from path (last component)
    if project_name is None:
        project_name = project_path_obj.name if project_path_obj.name else "Project"
    
    logger.info(f"Starting multi-language project analysis: {project_path_str}")
    logger.info(f"Project path exists: {project_path_obj.exists()}")
    logger.info(f"Project path is directory: {project_path_obj.is_dir()}")
    
    if project_path_obj.is_dir():
        # List immediate contents
        try:
            contents = list(project_path_obj.iterdir())
            logger.info(f"Project directory contents: {[str(p.name) for p in contents]}")
        except Exception as e:
            logger.warning(f"Could not list directory contents: {e}")

    # Initialize parsers
    py_parser = CodeParser(project_dir=project_path_str)
    regex_parser = SimpleRegexParser(project_dir=project_path_str)
    doc_parser = DocumentationParser(directory=project_path_str)
    comparator = Comparator()

    # Stats counters
    total_elements: int = 0
    classes_count: int = 0
    functions_count: int = 0
    methods_count: int = 0
    languages_found: set = set()
    checked_samples: int = 0
    issues: List[str] = []

    # Load all documentation once
    all_docs = doc_parser.parse_directory()

    # Try regex parser first (works for all languages)
    logger.info("Analyzing project with regex-based parser (multi-language support)...")
    try:
        code_elements = regex_parser.analyze_directory()
        
        for el in code_elements:
            total_elements += 1
            t = el.get("type")
            if t == "class":
                classes_count += 1
            elif t == "function":
                functions_count += 1
            elif t == "method":
                methods_count += 1
            
            lang = el.get("language", "unknown")
            if lang != "unknown":
                languages_found.add(lang)
        
        # Compare with documentation
        comparison = comparator.compare(code_elements, all_docs)
        if comparison:
            issues.extend(comparison)
        
        checked_samples = len([e for e in code_elements if e.get("file")])
        
        if total_elements > 0:
            logger.info(f"Regex parser found {total_elements} elements in {len(languages_found)} languages")
        else:
            # Regex found nothing, try Python parser for .py files
            logger.warning("Regex parser found no elements, trying Python AST parser")
            raise ValueError("Regex parser returned no elements")
    
    except Exception as e:
        logger.warning(f"Tree-sitter analysis failed, falling back to Python parser: {e}")
        # Reset counters for fallback
        total_elements = 0
        classes_count = 0
        functions_count = 0
        methods_count = 0
        checked_samples = 0
        languages_found = set()
        issues = []
        
        # Fallback to Python-only parser
        py_files = list(project_path_obj.rglob("*.py"))
        logger.info(f"Fallback: Found {len(py_files)} Python files to analyze")
        
        for file_path in py_files:
            file_str = str(file_path)
            try:
                code_info = py_parser.analyze_file(file_str)
                
                for el in code_info:
                    total_elements += 1
                    t = el.get("type")
                    if t == "class":
                        classes_count += 1
                    elif t == "function":
                        functions_count += 1
                    elif t == "method":
                        methods_count += 1
                
                comparison = comparator.compare(code_info, all_docs)
                if comparison:
                    issues.extend(comparison)
                
                checked_samples += 1
            except Exception as ex:
                logger.debug(f"Error parsing {file_str}: {ex}")
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
        "project_name": project_name,
        "project_path": project_path_str,
        "languages": sorted(list(languages_found)) if languages_found else ["python"],
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