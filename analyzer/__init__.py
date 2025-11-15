import importlib
from typing import Any, Dict, List

# local modules (package)
from .code_parser import CodeParser
from .doc_parser import DocumentationParser
from .comparator import Comparator

# Lazy load langchain when needed
_LLM_AVAILABLE = False
_llm = None
_prompt = None

def _init_llm():
    global _LLM_AVAILABLE, _llm, _prompt
    if _LLM_AVAILABLE:
        return
    try:
        llms_mod = importlib.import_module("langchain.llms")
        prompts_mod = importlib.import_module("langchain.prompts")
        OpenAI = getattr(llms_mod, "OpenAI")
        PromptTemplate = getattr(prompts_mod, "PromptTemplate")
        _llm = OpenAI(temperature=0)
        _prompt = PromptTemplate(
            input_variables=["code_snippet"],
            template="Analyze the following code for documentation inconsistencies:\n\n{code_snippet}"
        )
        _LLM_AVAILABLE = True
    except Exception:
        _LLM_AVAILABLE = False

def analyze_project(project_path: str) -> Dict[str, Any]:
    """
    Analyze a project directory for documentation consistency.
    Uses local parsers/comparator and, if available, an LLM to augment results.
    Returns a dict with status, checked_samples and issues.
    """
    cp = CodeParser(project_path)
    dp = DocumentationParser(project_path)
    code_elements = cp.analyze_directory()
    docs = dp.read_docs()
    comparator = Comparator(code_elements, docs)
    issues = comparator.check_consistency()

    # Try to augment analysis with LLM if available
    _init_llm()
    if _LLM_AVAILABLE and _llm is not None and _prompt is not None:
        # Create a compact code sample for the LLM
        sample_snippets = []
        for el in code_elements[:10]:
            name = el.get("name")
            doc = el.get("doc") or "<no-doc>"
            snippet = f"{el.get('type')} {name} - doc: {doc}"
            sample_snippets.append(snippet)
        payload = "\n".join(sample_snippets) or "no samples"
        formatted = _prompt.format(code_snippet=payload)
        try:
            llm_out = _llm(formatted)
        except Exception:
            try:
                llm_out = _llm.generate([formatted])
            except Exception:
                llm_out = "LLM invocation failed."

        return {
            "status": "ok",
            "mode": "llm_augmented",
            "checked_samples": len(code_elements),
            "issues": issues,
            "llm_analysis": str(llm_out)
        }
    else:
        return {
            "status": "fallback",
            "mode": "deterministic",
            "checked_samples": len(code_elements),
            "issues": issues
        }