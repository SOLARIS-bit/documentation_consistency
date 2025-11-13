# main.py
import streamlit as st
from analyzer import analyze_project
from data_generator import generate_synthetic_data

st.set_page_config(page_title="🧠 Documentation Consistency Assistant", layout="wide")

# --- Titre et description ---
st.title("🧠 Documentation Consistency Assistant")
st.write("Analyse la cohérence entre le code source et la documentation d’un projet.")

# --- Section Upload ---
st.subheader("📂 Importer ton projet")

code_file = st.file_uploader("Fichier de code (.py, .zip, .txt)", type=["py", "zip", "txt"])
doc_file = st.file_uploader("Fichier de documentation (.md, .txt, .pdf)", type=["md", "txt", "pdf"])

# --- Analyse réelle ---
if st.button("🔍 Lancer l'analyse"):
    if code_file and doc_file:
        code_text = code_file.read().decode("utf-8", errors="ignore")
        doc_text = doc_file.read().decode("utf-8", errors="ignore")

        with st.spinner("Analyse IA en cours... ⏳"):
            result = analyze_project(code_text, doc_text)
        st.success("✅ Analyse terminée !")
        st.write(result)
    else:
        st.warning("⚠️ Merci d'importer à la fois un fichier de code et de documentation.")

# --- Données de test SynthCity ---
st.subheader("🧪 Tester avec des données synthétiques")

if st.button("Générer un exemple de projet fictif"):
    with st.spinner("Création d’un exemple synthétique..."):
        example = generate_synthetic_data()
    st.success("Exemple synthétique généré ✅")
    st.code(example["code"], language="python")
    st.markdown(example["docs"])
    st.json(example["synthetic_data"])
