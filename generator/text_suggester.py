import importlib
from typing import Any, Dict, Callable

# Initialize the function variable
suggest_text_improvements: Callable[[str], Any]

# Try dynamic import of langchain components; provide a lightweight fallback.
try:
    llms_mod = importlib.import_module("langchain.llms")
    prompts_mod = importlib.import_module("langchain.prompts")

    OpenAI = getattr(llms_mod, "OpenAI")
    PromptTemplate = getattr(prompts_mod, "PromptTemplate")

    llm = OpenAI(temperature=0)
    prompt = PromptTemplate(
        input_variables=["doc_text"],
        template="Suggest improvements for the following documentation:\n{doc_text}"
    )

    def _langchain_implementation(doc_text: str) -> Any:
        """
        Use langchain/OpenAI to suggest improvements for documentation.
        """
        formatted = prompt.format(doc_text=doc_text)
        try:
            return llm(formatted)
        except Exception:
            try:
                return llm.generate([formatted])
            except Exception:
                return {"error": "LLM invocation failed at runtime."}
    
    # Assign the primary implementation
    suggest_text_improvements = _langchain_implementation

except Exception:
    def _fallback_implementation(doc_text: str) -> str:
        """
        Analyse locale intelligente sans IA pour processeurs ARM.
        Prend la liste des 'issues' et génère des conseils textuels.
        """
        issues_list = doc_text.split('\n')
        missing_count = len([i for i in issues_list if i.strip()])
        
        if missing_count == 0:
            return "✅ Your documentation is perfectly synced with your code. No improvements needed!"

        # Construction d'un conseil personnalisé
        suggestion = f"### 💡 Local Analysis: {missing_count} issues found\n\n"
        
        # Pour les grands projets/librairies avec beaucoup d'issues
        if missing_count > 50:
            suggestion += "This appears to be a large library or complex project. Many internal functions and classes are not documented in the main README, which is normal. Focus on documenting the public API.\n\n"
            suggestion += "Recommendations for large projects:\n"
            suggestion += "- Document only public classes and functions in the main README\n"
            suggestion += "- Use separate API documentation for internal components\n"
            suggestion += "- Consider using tools like Sphinx for comprehensive documentation\n\n"
            return suggestion
        
        # Analyse des types de problèmes pour petits projets
        missing_classes = sum(1 for issue in issues_list if "MISSING_DOC_CLASS" in issue)
        missing_methods = sum(1 for issue in issues_list if "MISSING_DOC_METHOD" in issue)
        missing_functions = sum(1 for issue in issues_list if "MISSING_DOC_FUNCTION" in issue)
        param_issues = sum(1 for issue in issues_list if "INCONSISTENCY_PARAM" in issue)
        
        suggestion += f"**Issue Breakdown:**\n"
        suggestion += f"- Classes missing: {missing_classes}\n"
        suggestion += f"- Methods missing: {missing_methods}\n"
        suggestion += f"- Functions missing: {missing_functions}\n"
        suggestion += f"- Parameter inconsistencies: {param_issues}\n\n"
        
        # Conseils spécifiques selon les types d'issues
        if missing_classes > 0:
            suggestion += "**Classes:** Add a section describing your main classes and their purpose.\n\n"
        
        if missing_methods > 0:
            suggestion += "**Methods:** Document public methods of your classes, especially those that are part of the API.\n\n"
        
        if missing_functions > 0:
            suggestion += "**Functions:** Ensure all public functions are listed with brief descriptions.\n\n"
        
        if param_issues > 0:
            suggestion += "**Parameters:** Make sure all function/method parameters are documented, especially optional ones.\n\n"
        
        # Si aucun problème spécifique, conseil général
        if missing_classes == 0 and missing_methods == 0 and missing_functions == 0 and param_issues == 0:
            suggestion += "Your documentation appears to be well-structured! Consider adding usage examples or API reference sections.\n\n"
            
        suggestion += "\n**Quick Fix**: Try to use a structured format in your README.md like:\n"
        suggestion += "```markdown\n## API Reference\n### Class Name\n- Method name: Description\n```"
        
        return suggestion
    
    # On assigne cette nouvelle implémentation
    suggest_text_improvements = _fallback_implementation