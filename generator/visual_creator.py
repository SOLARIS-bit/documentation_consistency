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
    Generate a multi-page PDF report with structured summary and charts.

    Pages:
    - Summary with key metrics
    - Issues by type (bar chart)
    - Documentation coverage (pie chart)
    - Top offenders by file (horizontal bar chart) if available

    Parameters
    ----------
    result : Dict[str, Any]
        Analyzer result dict including 'issues', 'checked_samples', 'mode',
        with optional 'stats' and 'issues_by_type'.
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

    with PdfPages(output_path) as pdf:
        # Page 1: Summary
        fig1 = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
        fig1.suptitle("Documentation Consistency Report", fontsize=20, color="#00C8FF")
        text_lines = [
            f"Status: {status.upper()}",
            f"Mode: {mode}",
            f"Files analyzed: {checked}",
            f"Total issues detected: {len(issues)}",
            f"Total elements detected: {total_elements}",
        ]
        y = 0.75
        for line in text_lines:
            fig1.text(0.08, y, line, fontsize=14)
            y -= 0.06
        pdf.savefig(fig1, bbox_inches='tight')
        plt.close(fig1)

        # Page 2: Issues by type (bar chart)
        labels = list(issues_by_type.keys())
        values = [issues_by_type[k] for k in labels]
        fig2, ax2 = plt.subplots(figsize=(11.69, 8.27))
        ax2.bar(labels, values, color=["#e74c3c", "#e67e22", "#f1c40f", "#3498db"])  # red, orange, yellow, blue
        ax2.set_title("Issues by Type", fontsize=18)
        ax2.set_ylabel("Count")
        ax2.set_xticklabels(labels, rotation=25, ha='right')
        ax2.grid(axis='y', alpha=0.2)
        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)

        # Page 3: Documentation coverage (pie)
        fig3, ax3 = plt.subplots(figsize=(11.69, 8.27))
        if total_elements > 0:
            ax3.pie(
                [documented, missing_total],
                labels=["Documented", "Missing"],
                autopct='%1.1f%%',
                colors=["#2ecc71", "#e74c3c"],
                startangle=140
            )
        ax3.set_title("Documentation Coverage (approx.)", fontsize=18)
        ax3.axis('equal')
        pdf.savefig(fig3, bbox_inches='tight')
        plt.close(fig3)

        # Page 4: Top offenders by file (optional)
        if file_counts:
            top_items = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            files = [f for f, _ in top_items]
            counts = [c for _, c in top_items]

            fig4, ax4 = plt.subplots(figsize=(11.69, 8.27))
            ax4.barh(range(len(files)), counts, color="#FF4B4B")
            ax4.set_yticks(range(len(files)))
            ax4.set_yticklabels(files)
            ax4.invert_yaxis()
            ax4.set_xlabel("Issues")
            ax4.set_title("Top Files with Missing/Inconsistent Docs", fontsize=18)
            pdf.savefig(fig4, bbox_inches='tight')
            plt.close(fig4)

    return output_path
