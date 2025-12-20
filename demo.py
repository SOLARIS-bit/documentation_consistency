#!/usr/bin/env python3
import zipfile
import shutil
from pathlib import Path

from project_analyzer import analyze_project
from generator.text_suggester import suggest_text_improvements
from generator.visual_creator import create_visual_summary


def print_header(title: str):
    print("\n" + "═" * 60)
    print(f"  {title}")
    print("═" * 60)


def unzip_project(zip_path: Path, extract_to: Path) -> Path:
    """Extract uploaded zipped project for analysis."""
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP not found: {zip_path}")

    if extract_to.exists():
        shutil.rmtree(extract_to)

    extract_to.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)

    return extract_to


def run_demo():

    print_header("📁 DEMO: Documentation Consistency Analyzer")

    # ---------------------------------------------------------
    # 1. Load project to analyze
    # ---------------------------------------------------------
    project_path = Path("example_project")

    if not project_path.exists():
        raise FileNotFoundError("❌ example_project folder not found.")

    print("🔍 Running project analysis...")
    result = analyze_project(str(project_path))

    # ---------------------------------------------------------
    # 2. Print analysis result
    # ---------------------------------------------------------
    print("\nAnalysis result:")
    print(result)

    issues = result.get("issues", [])

    if issues:
        print("\n📌 Issues detected:")
        for issue in issues:
            print(" -", issue)
    else:
        print("\n✨ No documentation issues found!")

    # ---------------------------------------------------------
    # 3. Generate text suggestions
    # ---------------------------------------------------------
    print("\n📝 Generating improvement suggestions...")

    issues_text = "\n".join(issues) if issues else "No documentation issues."

    suggestions = suggest_text_improvements(issues_text)

    print("\nSuggestions:")
    print(suggestions)

    # ---------------------------------------------------------
    # 4. Generate visual summary
    # ---------------------------------------------------------
    print("\n🎨 Generating visual summary...")

    output_path = "output.png"
    create_visual_summary(result, output_path=output_path)

    print(f"Visual created: {output_path}")

    print("\n✅ Demo completed successfully!")
    print("Run `xdg-open output.png` to open the summary image.")


if __name__ == "__main__":
    run_demo()
