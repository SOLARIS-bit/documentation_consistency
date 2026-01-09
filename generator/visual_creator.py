from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Any
import textwrap
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# If fonts are missing, we fall back to a default PIL font
def _load_font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_visual_summary(result: Dict[str, Any], output_path: str = "output.png") -> str:
    """
    Create a dark-themed HD visual summary (1920×1080) of the analysis result.

    Parameters
    ----------
    result : Dict[str, Any]
        {
            "status": "ok",
            "issues": [...],
            "checked_samples": int,
            "mode": "deterministic"
        }
    output_path : str
        Output image filename.

    Returns
    -------
    str : Path to the generated image.
    """

    # ====== THEME COLORS ======
    BG = (5, 5, 5)                    # Black background
    CARD_BG = (24, 24, 24)            # Dark gray panel
    TITLE_COLOR = (0, 200, 255)       # Cyan accent
    OK_COLOR = (0, 200, 0)            # Green
    WARN_COLOR = (255, 180, 0)        # Orange
    ERROR_COLOR = (255, 80, 80)       # Red
    TEXT_COLOR = (230, 230, 230)      # Light gray text

    # ====== SETUP HD CANVAS ======
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ====== LOAD FONTS ======
    font_title = _load_font(70)
    font_header = _load_font(40)
    font_text = _load_font(32)

    # ====== TITLE ======
    title = "Documentation Consistency Report"
    draw.text((100, 60), title, font=font_title, fill=TITLE_COLOR)

    # ====== CARD BACKGROUND ======
    # Rounded rectangle fallback using manual corners
    card_margin = 80
    card_x1 = card_margin
    card_y1 = 180
    card_x2 = W - card_margin
    card_y2 = H - card_margin

    # Large rounded panel
    draw.rounded_rectangle(
        [(card_x1, card_y1), (card_x2, card_y2)],
        radius=50,
        fill=CARD_BG
    )

    # ====== STATUS SECTION ======
    status = result.get("status", "unknown")
    issues = result.get("issues", [])
    checked = result.get("checked_samples", 0)
    mode = result.get("mode", "unknown")

    # Status color
    status_color = OK_COLOR if status == "ok" else ERROR_COLOR

    y = card_y1 + 40
    draw.text(
        (card_x1 + 40, y),
        f"Status: {status.upper()}",
        font=font_header,
        fill=status_color,
    )
    y += 70

    # Checked samples & Mode
    draw.text(
        (card_x1 + 40, y),
        f"Checked samples: {checked}",
        font=font_text,
        fill=TEXT_COLOR,
    )
    y += 45

    draw.text(
        (card_x1 + 40, y),
        f"Mode: {mode}",
        font=font_text,
        fill=TEXT_COLOR,
    )
    y += 80

    # ====== ISSUES SECTION ======
    draw.text(
        (card_x1 + 40, y),
        "Issue Summary:",
        font=font_header,
        fill=TITLE_COLOR,
    )
    y += 65

    if not issues:
        draw.text(
            (card_x1 + 60, y),
            "✔ No missing documentation!",
            font=font_text,
            fill=OK_COLOR,
        )
    else:
        # Calculate breakdown
        missing_classes = sum(1 for i in issues if "MISSING_DOC_CLASS" in i)
        missing_methods = sum(1 for i in issues if "MISSING_DOC_METHOD" in i)
        missing_functions = sum(1 for i in issues if "MISSING_DOC_FUNCTION" in i)
        param_issues = sum(1 for i in issues if "INCONSISTENCY_PARAM" in i)
        
        # Display breakdown
        breakdown_lines = [
            f"Total Issues: {len(issues)}",
            f"Classes Missing: {missing_classes}",
            f"Methods Missing: {missing_methods}",
            f"Functions Missing: {missing_functions}",
            f"Parameter Issues: {param_issues}"
        ]
        
        for line in breakdown_lines:
            draw.text(
                (card_x1 + 60, y),
                line,
                font=font_text,
                fill=WARN_COLOR,
            )
            y += 45

    # Save image
    img.save(output_path)
    return output_path


def create_pdf_report(result: Dict[str, Any], output_path: str = "analysis_report.pdf") -> str:
    """
    Generate a multi-page professional PDF report with header, styling, and charts.

    Pages:
    - Cover page with header/logo styling, project name, and summary metrics
    - Issues by type (bar chart)
    - Documentation coverage (pie chart)
    - Top offenders by file (horizontal bar chart)
    - Per-module breakdown (if sufficient data)

    Parameters
    ----------
    result : Dict[str, Any]
        Analyzer result dict including 'issues', 'checked_samples', 'mode',
        'project_name', with optional 'stats' and 'issues_by_type'.
    output_path : str
        Destination PDF path.

    Returns
    -------
    str : Path to the generated PDF.
    """

    issues: List[str] = result.get("issues", [])
    checked: int = int(result.get("checked_samples", 0))
    status: str = str(result.get("status", "unknown"))
    mode: str = str(result.get("mode", "unknown"))
    project_name: str = str(result.get("project_name", "Project"))

    stats: Dict[str, Any] = result.get("stats", {})
    issues_by_type: Dict[str, int] = result.get("issues_by_type", {})

    # Fallback compute if breakdown missing
    if not issues_by_type:
        issues_by_type = {
            "MISSING_DOC_CLASS": sum(1 for i in issues if "MISSING_DOC_CLASS" in i),
            "MISSING_DOC_METHOD": sum(1 for i in issues if "MISSING_DOC_METHOD" in i),
            "MISSING_DOC_FUNCTION": sum(1 for i in issues if "MISSING_DOC_FUNCTION" in i),
            "INCONSISTENCY_PARAM": sum(1 for i in issues if "INCONSISTENCY_PARAM" in i),
        }

    total_elements = int(stats.get("total_elements", 0))
    missing_total = (
        issues_by_type.get("MISSING_DOC_CLASS", 0)
        + issues_by_type.get("MISSING_DOC_METHOD", 0)
        + issues_by_type.get("MISSING_DOC_FUNCTION", 0)
    )
    documented = max(total_elements - missing_total, 0) if total_elements else 0

    # Build top offenders by file from issue strings ("| file: <path>")
    file_counts: Dict[str, int] = {}
    for msg in issues:
        if "| file:" in msg:
            try:
                part = msg.split("| file:", 1)[1].strip()
                file_key = part.strip()
                if file_key:
                    file_counts[file_key] = file_counts.get(file_key, 0) + 1
            except Exception:
                continue

    # Extract module-level grouping (first component of file path before /)
    module_counts: Dict[str, int] = {}
    for fpath, cnt in file_counts.items():
        module = fpath.split("/")[0] if "/" in fpath else fpath.split(".")[0]
        module_counts[module] = module_counts.get(module, 0) + cnt

    # Calculate score
    issues_per_file = len(issues) / max(checked, 1)
    if checked < 5:
        score = max(0, 100 - (issues_per_file * 20))
    else:
        score = max(0, 100 - (issues_per_file * 10))

    with PdfPages(output_path) as pdf:
        # --- Page 1: Cover with header/logo styling and PROJECT NAME ---
        fig1 = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
        fig1.patch.set_facecolor('#0a0a0a')
        
        # Header bar with gradient effect (simulated with rectangle)
        ax_header = fig1.add_axes([0, 0.85, 1, 0.15])
        ax_header.set_facecolor('#1a1a1a')
        ax_header.set_xlim(0, 1)
        ax_header.set_ylim(0, 1)
        ax_header.axis('off')
        ax_header.text(0.05, 0.5, "📚 Documentation Consistency Assistant", 
                      fontsize=24, color="#00C8FF", weight='bold', va='center')
        ax_header.text(0.95, 0.5, f"Score: {score:.1f}%", 
                      fontsize=20, color="#2ecc71" if score > 80 else "#e74c3c", 
                      weight='bold', ha='right', va='center')

        # PROJECT NAME prominently displayed
        fig1.text(0.5, 0.78, f"Project: {project_name}", 
                 ha='center', fontsize=28, color="#00C8FF", weight='bold', style='italic')

        # Summary section
        text_lines = [
            ("Analysis Summary", 18, "#00C8FF", 'bold'),
            ("", 10, "#fff", 'normal'),
            (f"Status: {status.upper()}", 14, "#2ecc71" if status == "ok" else "#e74c3c", 'normal'),
            (f"Analysis Mode: {mode}", 14, "#fff", 'normal'),
            (f"Files Analyzed: {checked}", 14, "#fff", 'normal'),
            (f"Total Elements Detected: {total_elements}", 14, "#fff", 'normal'),
            (f"Issues Found: {len(issues)}", 14, "#e67e22" if len(issues) > 0 else "#2ecc71", 'normal'),
            ("", 10, "#fff", 'normal'),
            ("Issue Breakdown:", 16, "#00C8FF", 'bold'),
            (f"  • Missing Classes: {issues_by_type.get('MISSING_DOC_CLASS', 0)}", 13, "#e74c3c", 'normal'),
            (f"  • Missing Methods: {issues_by_type.get('MISSING_DOC_METHOD', 0)}", 13, "#e67e22", 'normal'),
            (f"  • Missing Functions: {issues_by_type.get('MISSING_DOC_FUNCTION', 0)}", 13, "#f1c40f", 'normal'),
            (f"  • Parameter Issues: {issues_by_type.get('INCONSISTENCY_PARAM', 0)}", 13, "#3498db", 'normal'),
        ]
        
        y = 0.70
        for text, size, color, weight in text_lines:
            fig1.text(0.08, y, text, fontsize=size, color=color, weight=weight)
            y -= 0.05
        
        # Footer
        fig1.text(0.5, 0.05, "Generated by Documentation Consistency Assistant • github.com/SOLARIS-bit/documentation_consistency", 
                 ha='center', fontsize=9, color='#666', style='italic')
        
        pdf.savefig(fig1, bbox_inches='tight', facecolor='#0a0a0a')
        plt.close(fig1)

        # --- Page 2: Issues by type (styled bar chart) ---
        labels = list(issues_by_type.keys())
        values = [issues_by_type[k] for k in labels]
        fig2, ax2 = plt.subplots(figsize=(11.69, 8.27))
        fig2.patch.set_facecolor('#0a0a0a')
        ax2.set_facecolor('#1a1a1a')
        
        bars = ax2.bar(labels, values, color=["#e74c3c", "#e67e22", "#f1c40f", "#3498db"], 
                       edgecolor='white', linewidth=1.5)
        ax2.set_title("Issues by Type", fontsize=20, color="#00C8FF", weight='bold', pad=20)
        ax2.set_ylabel("Count", fontsize=14, color='white')
        ax2.set_xticklabels(labels, rotation=25, ha='right', fontsize=12, color='white')
        ax2.tick_params(colors='white')
        ax2.grid(axis='y', alpha=0.2, color='white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', color='white', fontsize=11)
        
        pdf.savefig(fig2, bbox_inches='tight', facecolor='#0a0a0a')
        plt.close(fig2)

        # --- Page 3: Documentation coverage (styled pie) ---
        fig3, ax3 = plt.subplots(figsize=(11.69, 8.27))
        fig3.patch.set_facecolor('#0a0a0a')
        ax3.set_facecolor('#1a1a1a')
        
        if total_elements > 0:
            wedges, texts, autotexts = ax3.pie(
                [documented, missing_total],
                labels=["Documented", "Missing"],
                autopct='%1.1f%%',
                colors=["#2ecc71", "#e74c3c"],
                startangle=140,
                textprops={'color': 'white', 'fontsize': 14, 'weight': 'bold'}
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(16)
                autotext.set_weight('bold')
        
        ax3.set_title("Documentation Coverage", fontsize=20, color="#00C8FF", weight='bold', pad=20)
        ax3.axis('equal')
        
        pdf.savefig(fig3, bbox_inches='tight', facecolor='#0a0a0a')
        plt.close(fig3)

        # --- Page 4: Top offenders by file ---
        if file_counts:
            top_items = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:12]
            files = [f for f, _ in top_items]
            counts = [c for _, c in top_items]

            fig4, ax4 = plt.subplots(figsize=(11.69, 8.27))
            fig4.patch.set_facecolor('#0a0a0a')
            ax4.set_facecolor('#1a1a1a')
            
            bars = ax4.barh(range(len(files)), counts, color="#FF4B4B", edgecolor='white', linewidth=1.5)
            ax4.set_yticks(range(len(files)))
            ax4.set_yticklabels(files, fontsize=11, color='white')
            ax4.invert_yaxis()
            ax4.set_xlabel("Issues", fontsize=14, color='white')
            ax4.set_title("Top Files with Documentation Issues", fontsize=20, color="#00C8FF", weight='bold', pad=20)
            ax4.tick_params(colors='white')
            ax4.grid(axis='x', alpha=0.2, color='white')
            ax4.spines['bottom'].set_color('white')
            ax4.spines['left'].set_color('white')
            ax4.spines['top'].set_visible(False)
            ax4.spines['right'].set_visible(False)
            
            # Add value labels
            for i, (bar, count) in enumerate(zip(bars, counts)):
                ax4.text(count + 0.5, i, str(count), va='center', color='white', fontsize=10)
            
            pdf.savefig(fig4, bbox_inches='tight', facecolor='#0a0a0a')
            plt.close(fig4)

        # --- Page 5: Per-module breakdown (if multiple modules) ---
        if len(module_counts) > 1:
            sorted_modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            modules = [m for m, _ in sorted_modules]
            mod_counts = [c for _, c in sorted_modules]

            fig5, ax5 = plt.subplots(figsize=(11.69, 8.27))
            fig5.patch.set_facecolor('#0a0a0a')
            ax5.set_facecolor('#1a1a1a')
            
            bars = ax5.barh(range(len(modules)), mod_counts, 
                           color=plt.cm.Spectral([i/len(modules) for i in range(len(modules))]),
                           edgecolor='white', linewidth=1.5)
            ax5.set_yticks(range(len(modules)))
            ax5.set_yticklabels(modules, fontsize=11, color='white')
            ax5.invert_yaxis()
            ax5.set_xlabel("Issues", fontsize=14, color='white')
            ax5.set_title("Issues by Module/Package", fontsize=20, color="#00C8FF", weight='bold', pad=20)
            ax5.tick_params(colors='white')
            ax5.grid(axis='x', alpha=0.2, color='white')
            ax5.spines['bottom'].set_color('white')
            ax5.spines['left'].set_color('white')
            ax5.spines['top'].set_visible(False)
            ax5.spines['right'].set_visible(False)
            
            for i, (bar, count) in enumerate(zip(bars, mod_counts)):
                ax5.text(count + 0.5, i, str(count), va='center', color='white', fontsize=10)
            
            pdf.savefig(fig5, bbox_inches='tight', facecolor='#0a0a0a')
            plt.close(fig5)

    return output_path
