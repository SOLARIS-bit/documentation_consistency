from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Any
import textwrap
import os


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
