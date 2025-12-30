import streamlit as st
from pathlib import Path
import tempfile
import shutil
import os
import zipfile

import pandas as pd
import matplotlib
matplotlib.use('Agg') # Force un backend non-interactif (crucial pour Chromebook)
import matplotlib.pyplot as plt

from project_analyzer import analyze_project
from generator.text_suggester import suggest_text_improvements
from generator.visual_creator import create_visual_summary

def generate_markdown_snippet(issues, result):
    snippet = "## 📝 Documentation Update\n\n"
    # On crée un dictionnaire pour retrouver les infos du code rapidement
    # Supposons que result_full['raw_data'] contient les éléments analysés
    
    for issue in issues:
        name = issue.replace("Missing documentation for: ", "")
        snippet += f"### `{name}`\n"
        snippet += "✅ **Status**: Detected in code, missing in docs.\n\n"
        snippet += "**Description**:\n*Add a brief overview of this component here.*\\n\n"
        snippet += "---\n"
    return snippet
# ---- Streamlit App ----
st.set_page_config(page_title="Documentation Consistency Analyzer", layout="wide")
st.title("📚 Documentation Consistency Analyzer")
st.markdown("""
Upload your Python project and optional documentation to check for missing documentation,
get suggestions, and generate visual and downloadable reports.
""")

# ---- Upload project folder (zip) ----
uploaded_project = st.file_uploader(
    "Upload your project as a ZIP file (or drag & drop)", type=["zip"]
)

uploaded_docs = st.file_uploader(
    "Upload additional documentation (Markdown / TXT ZIP)", type=["zip"]
)

if uploaded_project:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract project ZIP
        zf = zipfile.ZipFile(uploaded_project)
        zf.extractall(tmpdir)

        # Extract documentation ZIP on top if provided
        if uploaded_docs:
            zf_docs = zipfile.ZipFile(uploaded_docs)
            zf_docs.extractall(tmpdir)

        st.success(f"Project extracted to: {tmpdir}")
        project_path = tmpdir

        # ---- Run analysis ----
        st.info("🔍 Running analysis...")
        result = analyze_project(project_path)
        issues = result.get("issues", [])
        checked_samples = result.get("checked_samples", 0)

        # ---- Summary metrics ----
        st.subheader("Analysis Summary")
        st.markdown(f"- **Status:** {result.get('status')}")
        st.markdown(f"- **Mode:** {result.get('mode')}")
        st.markdown(f"- **Files analyzed:** {checked_samples}")
        st.markdown(f"- **Total issues detected:** {len(issues)}")
        
        # ---- Health Score Gauge ----
        # Calculate score based on issues per file ratio
        issues_per_file = len(issues) / max(checked_samples, 1)
        # For small projects (<5 files), be strict; for larger, more lenient
        if checked_samples < 5:
            score = max(0, 100 - (issues_per_file * 20))
        else:
            score = max(0, 100 - (issues_per_file * 10))
        
        if score > 80:
            st.success(f"🏅 Documentation Score: {score:.1f}% - Excellent!")
        elif score > 50:
            st.warning(f"⚠️ Documentation Score: {score:.1f}% - Needs work.")
        else:
            st.error(f"🚨 Documentation Score: {score:.1f}% - Poor consistency.")

        # ---- Issue Summary ----
        if issues:
            st.subheader("📊 Issue Summary")
            missing_classes = sum(1 for i in issues if "MISSING_DOC_CLASS" in i)
            missing_methods = sum(1 for i in issues if "MISSING_DOC_METHOD" in i)
            missing_functions = sum(1 for i in issues if "MISSING_DOC_FUNCTION" in i)
            param_issues = sum(1 for i in issues if "INCONSISTENCY_PARAM" in i)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Missing Classes", missing_classes)
            with col2:
                st.metric("Missing Methods", missing_methods)
            with col3:
                st.metric("Missing Functions", missing_functions)
            with col4:
                st.metric("Param Issues", param_issues)
        if issues:
            st.subheader("📌 Issues Detected")
            for i in issues:
                if "MISSING_DOC_CLASS" in i:
                    icon = "🏗️"  # Classe manquante
                    color = "red"
                elif "MISSING_DOC_METHOD" in i:
                    icon = "🔧"  # Méthode manquante
                    color = "orange"
                elif "MISSING_DOC_FUNCTION" in i:
                    icon = "⚙️"  # Fonction manquante
                    color = "orange"
                elif "INCONSISTENCY_PARAM" in i:
                    icon = "📝"  # Paramètre manquant
                    color = "blue"
                elif "VERSION_ERROR" in i:
                    icon = "❌"  # Erreur critique de version
                    color = "red"
                else:
                    icon = "⚠️"  # Manque de doc générique
                    color = "gray"
            
                st.markdown(f"<span style='color:{color}'>{icon} {i}</span>", unsafe_allow_html=True)
        # ---- Text suggestions ----
        st.subheader("📝 Improvement Suggestions")
        summary_text = "\n".join(issues)
        suggestions = suggest_text_improvements(summary_text)

        # Si suggestions est une string (avec notre nouveau code), on l'affiche directement
        st.markdown(suggestions)
        # ---- Module-level coverage chart ----
        st.subheader("📊 Documentation Health Map")
        modules = [i.split(".")[0] for i in issues] if issues else []
        df = pd.DataFrame({"module": modules})
        
        if not df.empty:
            coverage_counts = df["module"].value_counts()
            
            # Style moderne
            plt.style.use('ggplot') 
            fig, ax = plt.subplots(figsize=(10, 4))
            coverage_counts.plot(kind="barh", ax=ax, color="#FF4B4B") # Rouge Streamlit
            
            ax.set_title("Missing Items per Module", fontsize=14, pad=20)
            ax.set_xlabel("Count", fontsize=12)
            ax.set_ylabel("Module", fontsize=12)
            plt.tight_layout()
            
            st.pyplot(fig, clear_figure=True)

        if not df.empty:
           # On nettoie les messages pour le graphique (enlever les icônes)
           df["clean_module"] = df["module"].str.replace("🟠", "").str.replace("⚠️", "").str.replace("❌", "").str.strip()
           coverage_counts = df["clean_module"].value_counts()
           plt.style.use('ggplot') 
           fig, ax = plt.subplots(figsize=(10, 4))
           coverage_counts.plot(kind="barh", ax=ax, color="#FF4B4B")
           ax.set_title("Issues per Category", fontsize=14, pad=20)
        # ---- Quick Fix Button ----
        if issues:
            st.subheader("🛠️ Quick Fix")
            if st.button("Generate Markdown for Missing Items"):
                fix_text = generate_markdown_snippet(issues, result)
                st.code(fix_text, language="markdown")
                st.info("👆 Copy this into your README.md to fix the issues!")

        # ---- Visual Summary ----
        st.subheader("🎨 Visual Summary")
        visual_path = create_visual_summary(result)
        st.image(visual_path, caption="Documentation Consistency Summary", width=1200)
    

        # ---- Downloadable report ----
        st.subheader("💾 Export Analysis")
        
        report_content = f"ANALYSIS REPORT\n{'='*20}\n"
        report_content += f"Issues found: {len(issues)}\n\n"
        report_content += "ISSUES:\n" + "\n".join(issues)
        report_content += f"\n\nSUGGESTIONS:\n{suggestions}"

        st.download_button(
            label="Download Full Text Report",
            data=report_content,
            file_name="documentation_report.txt",
            mime="text/plain"
        )
__version__ = "1.0.0"