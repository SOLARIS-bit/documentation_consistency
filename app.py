# app.py
import streamlit as st
from pathlib import Path
import tempfile
import shutil
import os
import zipfile

import pandas as pd
import matplotlib.pyplot as plt

from project_analyzer import analyze_project
from generator.text_suggester import suggest_text_improvements
from generator.visual_creator import create_visual_summary

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

        # ---- Display issues with color-coded warnings ----
        if issues:
            st.subheader("📌 Issues Detected")
            for i in issues:
                st.markdown(f"<span style='color:red'>⚠️ {i}</span>", unsafe_allow_html=True)
        else:
            st.success("No missing documentation detected ✅")

        # ---- Text suggestions ----
        st.subheader("📝 Improvement Suggestions")
        summary_text = "\n".join(issues)
        suggestions = suggest_text_improvements(summary_text)
        st.write(suggestions)

        # ---- Module-level coverage chart ----
        st.subheader("📊 Documentation Coverage per Module")
        # Build a simple coverage dataframe
        modules = [i.split(".")[0] for i in issues] if issues else []
        df = pd.DataFrame({"module": modules})
        coverage_counts = df["module"].value_counts() if not df.empty else pd.DataFrame({"module":[], "count":[]})
        fig, ax = plt.subplots()
        coverage_counts.plot(kind="bar", ax=ax, color="tomato")
        ax.set_title("Modules with Missing Documentation")
        ax.set_xlabel("Module")
        ax.set_ylabel("Number of Missing Items")
        st.pyplot(fig)

        # ---- Visual Summary ----
        st.subheader("🎨 Visual Summary")
        visual_path = create_visual_summary(result)
        st.image(visual_path, caption="Documentation Consistency Summary", width=1200)

        # ---- Downloadable report ----
        st.subheader("💾 Download Report")
        with open(visual_path, "rb") as f:
            st.download_button(
                label="Download Visual PNG",
                data=f,
                file_name="documentation_summary.png",
                mime="image/png"
            )

        st.success("✅ Analysis completed!")
