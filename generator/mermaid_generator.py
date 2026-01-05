"""
Mermaid diagram generator for architecture and analysis visualization.
Generates Mermaid-format diagrams showing project structure and dependencies.
"""

from typing import Dict, List, Any, Optional
import json


class MermaidGenerator:
    """Generate Mermaid diagrams from code structure analysis."""

    @staticmethod
    def generate_project_structure(code_elements: List[Dict[str, Any]]) -> str:
        """
        Generate a Mermaid class diagram showing project structure.
        
        Parameters
        ----------
        code_elements : List[Dict[str, Any]]
            List of code elements from CodeParser with structure information
            
        Returns
        -------
        str : Mermaid diagram in markdown format
        """
        classes = [e for e in code_elements if e.get("type") == "class"]
        
        if not classes:
            return "graph TD\n    A[No classes found]\n"
        
        # Group by file
        files_to_classes: Dict[str, List[str]] = {}
        for cls in classes:
            file_name = cls.get("file", "unknown").replace("\\", "/").split("/")[-1]
            if file_name not in files_to_classes:
                files_to_classes[file_name] = []
            files_to_classes[file_name].append(cls.get("name", "Unknown"))
        
        mermaid = "graph TD\n"
        
        for file_name, class_names in files_to_classes.items():
            file_node = file_name.replace(".", "_")
            mermaid += f'    {file_node}["{file_name}"]\n'
            
            for class_name in class_names:
                class_node = f"{file_node}_{class_name}"
                mermaid += f'    {class_node}["{class_name}"]\n'
                mermaid += f'    {file_node} --> {class_node}\n'
        
        return mermaid

    @staticmethod
    def generate_analysis_flow(result: Dict[str, Any]) -> str:
        """
        Generate a Mermaid flowchart showing the analysis process and results.
        
        Parameters
        ----------
        result : Dict[str, Any]
            Analysis result dictionary with status, issues, samples
            
        Returns
        -------
        str : Mermaid flowchart diagram
        """
        issues_count = len(result.get("issues", []))
        checked_samples = result.get("checked_samples", 0)
        status = result.get("status", "unknown")
        
        # Calculate health score
        issues_per_file = issues_count / max(checked_samples, 1)
        if checked_samples < 5:
            health_score = max(0, 100 - (issues_per_file * 20))
        else:
            health_score = max(0, 100 - (issues_per_file * 10))
        
        # Determine status color
        if health_score >= 80:
            status_color = "green"
            health_status = "Excellent"
        elif health_score >= 60:
            status_color = "yellow"
            health_status = "Good"
        else:
            status_color = "red"
            health_status = "Needs Work"
        
        mermaid = """graph TD
    A["📁 Project Analysis"] --> B["🔍 Parse Code<br/>Extract Functions/Classes"]
    A --> C["📚 Parse Documentation<br/>Read Markdown/Txt"]
    
    B --> D["⚖️ Comparison Engine<br/>Match Code vs Docs"]
    C --> D
    
    D --> E{"Issues Found?"}
    E -->|Yes| F["⚠️ Generate Suggestions<br/>LLM or Heuristics"]
    E -->|No| G["✅ Documentation Consistent"]
    
    F --> H["📊 Create Reports<br/>PNG + Markdown + Diagrams"]
    G --> H
    
    H --> I["📈 Health Metrics"]
    I --> J["{status_line}"]
    
    style A fill:#2a3f5f
    style D fill:#0066cc
    style F fill:#ff9933
    style G fill:#00cc00
    style H fill:#9933ff
    style J fill:{status_color}

    classDef metric fill:#333,stroke:#666,color:#fff
    class I,J metric
"""
        
        status_line = f"Health: {health_score:.0f}% | Files: {checked_samples} | Issues: {issues_count} | Status: {health_status}"
        mermaid = mermaid.format(status_line=status_line, status_color=status_color)
        
        return mermaid

    @staticmethod
    def generate_issues_breakdown(issues: List[str]) -> str:
        """
        Generate a Mermaid pie chart showing issue distribution.
        
        Parameters
        ----------
        issues : List[str]
            List of issue strings
            
        Returns
        -------
        str : Mermaid pie chart diagram
        """
        if not issues:
            return "pie title Issue Breakdown\n    No Issues: 100\n"
        
        # Categorize issues
        categories = {
            "Missing Docs": 0,
            "Parameter Mismatch": 0,
            "Version Mismatch": 0,
            "Other": 0
        }
        
        for issue in issues:
            if "MISSING_DOC" in issue or "Missing documentation" in issue:
                categories["Missing Docs"] += 1
            elif "INCONSISTENCY_PARAM" in issue or "Parameter" in issue:
                categories["Parameter Mismatch"] += 1
            elif "VERSION" in issue or "version" in issue:
                categories["Version Mismatch"] += 1
            else:
                categories["Other"] += 1
        
        mermaid = "pie title Issue Distribution\n"
        for category, count in categories.items():
            if count > 0:
                mermaid += f'    "{category}": {count}\n'
        
        return mermaid

    @staticmethod
    def generate_file_coverage(code_elements: List[Dict[str, Any]]) -> str:
        """
        Generate a Mermaid bar chart showing documentation coverage by file.
        
        Parameters
        ----------
        code_elements : List[Dict[str, Any]]
            List of code elements with documentation info
            
        Returns
        -------
        str : Mermaid XY chart data
        """
        # Group by file and count documented vs undocumented
        file_coverage: Dict[str, Dict[str, int]] = {}
        
        for element in code_elements:
            if element.get("type") == "version":
                continue
            
            file_name = element.get("file", "unknown").replace("\\", "/").split("/")[-1]
            
            if file_name not in file_coverage:
                file_coverage[file_name] = {"documented": 0, "undocumented": 0}
            
            if element.get("doc"):
                file_coverage[file_name]["documented"] += 1
            else:
                file_coverage[file_name]["undocumented"] += 1
        
        if not file_coverage:
            return "graph LR\n    A[No coverage data]\n"
        
        # Create table visualization
        mermaid = "graph TD\n"
        mermaid += '    A["📋 Documentation Coverage by File"]\n'
        
        for file_name, counts in sorted(file_coverage.items()):
            total = counts["documented"] + counts["undocumented"]
            percentage = (counts["documented"] / total * 100) if total > 0 else 0
            
            node_id = file_name.replace(".", "_").replace("/", "_")
            label = f"{file_name}<br/>{counts['documented']}/{total} documented ({percentage:.0f}%)"
            
            # Color based on coverage
            if percentage >= 80:
                color = "#00cc00"  # Green
            elif percentage >= 50:
                color = "#ffcc00"  # Yellow
            else:
                color = "#cc0000"  # Red
            
            mermaid += f'    {node_id}["{label}"]\n'
            mermaid += f'    style {node_id} fill:{color}\n'
            mermaid += f'    A --> {node_id}\n'
        
        return mermaid

    @staticmethod
    def generate_complete_report(result: Dict[str, Any], code_elements: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate a complete set of Mermaid diagrams for a full report.
        
        Parameters
        ----------
        result : Dict[str, Any]
            Analysis result from project_analyzer
        code_elements : List[Dict[str, Any]]
            Code elements extracted from source files
            
        Returns
        -------
        Dict[str, str] : Dictionary of diagram names and their Mermaid code
        """
        return {
            "analysis_flow": MermaidGenerator.generate_analysis_flow(result),
            "project_structure": MermaidGenerator.generate_project_structure(code_elements),
            "issues_breakdown": MermaidGenerator.generate_issues_breakdown(result.get("issues", [])),
            "file_coverage": MermaidGenerator.generate_file_coverage(code_elements),
        }

    @staticmethod
    def to_markdown(diagrams: Dict[str, str]) -> str:
        """
        Convert Mermaid diagrams to markdown format for embedding.
        
        Parameters
        ----------
        diagrams : Dict[str, str]
            Dictionary of diagram names and Mermaid code
            
        Returns
        -------
        str : Markdown formatted diagrams
        """
        markdown = "# 📊 Documentation Analysis Diagrams\n\n"
        
        if "analysis_flow" in diagrams:
            markdown += "## Analysis Flow\n\n```mermaid\n"
            markdown += diagrams["analysis_flow"]
            markdown += "\n```\n\n"
        
        if "project_structure" in diagrams:
            markdown += "## Project Structure\n\n```mermaid\n"
            markdown += diagrams["project_structure"]
            markdown += "\n```\n\n"
        
        if "issues_breakdown" in diagrams:
            markdown += "## Issue Distribution\n\n```mermaid\n"
            markdown += diagrams["issues_breakdown"]
            markdown += "\n```\n\n"
        
        if "file_coverage" in diagrams:
            markdown += "## Documentation Coverage by File\n\n```mermaid\n"
            markdown += diagrams["file_coverage"]
            markdown += "\n```\n\n"
        
        return markdown


# Convenience function for backwards compatibility
def generate_mermaid_diagrams(result: Dict[str, Any], code_elements: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate all Mermaid diagrams from analysis result."""
    return MermaidGenerator.generate_complete_report(result, code_elements)
