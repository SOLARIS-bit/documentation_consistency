
from langchain.prompts import PromptTemplate

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

    llm = OpenAI(temperature=0.2)
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(code=code_text, docs=doc_text)
