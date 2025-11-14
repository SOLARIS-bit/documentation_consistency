from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence


def analyze_project(code_text: str, doc_text: str) -> str:
    prompt = PromptTemplate.from_template("""
Tu es un assistant technique expert.
Compare le code ci-dessous avec sa documentation et identifie les incohérences.

--- CODE ---
{code}

--- DOCUMENTATION ---
{docs}

Liste les incohérences et propose des corrections.
""")

    llm = ChatOpenAI(
        model="gpt-4o-mini",  # compatible, rapide, pas cher
        temperature=0.2
    )

    # Nouveau pipeline LCEL (LangChain Expression Language)
    chain = RunnableSequence(
        prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke({"code": code_text, "docs": doc_text})
