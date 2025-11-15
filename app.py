from analyzer import analyze_project
from generator.text_suggester import suggest_text_improvements
from generator.visual_creator import create_visual

def main():
    project_path = "./data"
    result = analyze_project(project_path)
    print("Analyse terminée :", result)

    suggestion = suggest_text_improvements("Example documentation text")
    print("Suggestion :", suggestion)

    visual_file = create_visual("Documentation summary")
    print("Visual créé :", visual_file)

if __name__ == "__main__":
    main()