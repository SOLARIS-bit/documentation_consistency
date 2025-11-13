import streamlit as st
from analyzer.code_parser import CodeParser
from analyzer.doc_parser import DocumentationParser
from analyzer.comparator import Comparator

st.set_page_config(page_title="Documentation Consistency Assistant", layout="wide")

st.title("📘 Documentation Consistency Assistant")
project_path = st.text_input("Dossier du projet à analyser :", "example_project")

if st.button("Analyser le projet"):
    code_parser = CodeParser(project_path)
    doc_parser = DocumentationParser(project_path)

    code_data = code_parser.analyze_directory()
    doc_data = doc_parser.read_docs()

    comparator = Comparator(code_data, doc_data)
    missing = comparator.check_consistency()

    st.subheader("⚠️ Éléments non documentés")
    if missing:
        for m in missing:
            st.write(f"- {m['type'].capitalize()} **{m['name']}** n'est pas mentionné dans la documentation.")
    else:
        st.success("✅ Toute la documentation semble à jour !")
