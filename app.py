import streamlit as st
from pathlib import Path
import tempfile
import shutil
import os
import zipfile
import logging
import json

import pandas as pd
import matplotlib
matplotlib.use('Agg') # Force un backend non-interactif (crucial pour Chromebook)
import matplotlib.pyplot as plt

from project_analyzer import analyze_project
from generator.text_suggester import suggest_text_improvements
from generator.visual_creator import create_visual_summary

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_FILE = "settings.json"
DEFAULT_CONFIG = {
    "max_file_size_mb": 50,
    "max_issues_shown": 100,
    "exclude_dirs": ["tests", "venv", "docs", ".git"],
    "llm_model": "gpt-4o-mini",
    "llm_temperature": 0.1,
    "github_timeout_seconds": 30
}

def load_config():
    """Load configuration from settings.json or use defaults."""
    if Path(CONFIG_FILE).exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
    return DEFAULT_CONFIG

CONFIG = load_config()

def validate_zip_file(uploaded_file, max_size_mb: int = None) -> tuple[bool, str]:
    """
    Validate uploaded ZIP file for security issues.
    
    Parameters
    ----------
    uploaded_file : UploadedFile
        Streamlit uploaded file object
    max_size_mb : int
        Maximum allowed file size in MB
        
    Returns
    -------
    tuple[bool, str] : (is_valid, error_message)
    """
    max_size_mb = max_size_mb or CONFIG.get("max_file_size_mb", 50)
    
    if uploaded_file is None:
        return False, "No file selected"
    
    # Check file size
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f"File too large: {file_size_mb:.1f}MB (max {max_size_mb}MB)"
    
    # Check ZIP structure
    try:
        with zipfile.ZipFile(uploaded_file) as zf:
            # Check for ZIP bombs (excessive compression ratios)
            total_uncompressed = 0
            max_file_size = 100 * 1024 * 1024  # 100MB per file limit
            
            for info in zf.infolist():
                # Check individual file size
                if info.file_size > max_file_size:
                    return False, f"File inside ZIP too large: {info.filename}"
                total_uncompressed += info.file_size
            
            # Check total uncompressed size (zip bomb detection)
            # Allow higher ratio for legitimate large projects (e.g., libraries with many small files)
            max_uncompressed = max_size_mb * 1024 * 1024 * 100  # 100x compression ratio (e.g., 5GB uncompressed for 50MB ZIP)
            if total_uncompressed > max_uncompressed:
                return False, f"ZIP content too large (zip bomb detected)"
            
            # Check for suspicious paths (directory traversal)
            for name in zf.namelist():
                if ".." in name or name.startswith("/"):
                    return False, f"Suspicious path in ZIP: {name}"
            
            logger.info(f"ZIP validation passed: {file_size_mb:.1f}MB")
            return True, ""
    
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file format"
    except Exception as e:
        return False, f"ZIP validation error: {str(e)}"

def safe_extract_zip(uploaded_file, extract_dir: Path) -> bool:
    """
    Safely extract ZIP file with validation.
    
    Parameters
    ----------
    uploaded_file : UploadedFile
        Streamlit uploaded file
    extract_dir : Path
        Target extraction directory
        
    Returns
    -------
    bool : True if extraction successful
    """
    is_valid, error_msg = validate_zip_file(uploaded_file)
    if not is_valid:
        logger.error(f"ZIP validation failed: {error_msg}")
        raise ValueError(error_msg)
    
    try:
        with zipfile.ZipFile(uploaded_file) as zf:
            zf.extractall(str(extract_dir))
        logger.info(f"Successfully extracted ZIP to {extract_dir}")
        return True
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise

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

# Show configuration info in sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown(f"- **Max file size:** {CONFIG.get('max_file_size_mb')}MB")
    st.markdown(f"- **Max issues shown:** {CONFIG.get('max_issues_shown')}")
    st.markdown(f"- **LLM Model:** {CONFIG.get('llm_model')}")

# ---- Upload project folder (zip) ----
st.markdown("### 📤 Upload Your Project")
uploaded_project = st.file_uploader(
    "Upload your project as a ZIP file (or drag & drop)", type=["zip"]
)

uploaded_docs = st.file_uploader(
    "Upload additional documentation (Markdown / TXT ZIP)", type=["zip"]
)

if uploaded_project:
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Extract project ZIP with validation
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()
            safe_extract_zip(uploaded_project, project_dir)
            
            # Extract documentation ZIP on top if provided
            if uploaded_docs:
                docs_dir = Path(tmpdir) / "docs"
                docs_dir.mkdir()
                safe_extract_zip(uploaded_docs, docs_dir)
                logger.info(f"Extracted {len(list(docs_dir.glob('**/*.md')))} documentation files")
            
            logger.info(f"Starting analysis of uploaded project")
            st.success(f"✅ Project extracted successfully")
            
            project_path = str(project_dir)

            # ---- Run analysis ----
            st.info("🔍 Running analysis...")
            try:
                result = analyze_project(project_path)
                logger.info(f"Analysis complete: {len(result.get('issues', []))} issues found")
            except Exception as e:
                logger.error(f"Analysis failed: {str(e)}")
                st.error(f"❌ Analysis failed: {str(e)}")
                st.stop()
            
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
                # Limit issues shown to config max
                max_issues = CONFIG.get("max_issues_shown", 100)
                for i in issues[:max_issues]:
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
                coverage_counts.plot(kind="barh", ax=ax, color="#FF4B4B")
                
                ax.set_title("Missing Items per Module", fontsize=14, pad=20)
                ax.set_xlabel("Count", fontsize=12)
                ax.set_ylabel("Module", fontsize=12)
                plt.tight_layout()
                
                st.pyplot(fig, clear_figure=True)

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
        
        except ValueError as e:
            st.error(f"❌ Validation error: {str(e)}")
            logger.error(f"Validation failed: {str(e)}")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)

__version__ = "2.1.0"