#!/usr/bin/env python3
"""
Analyze all Python projects and generate a comprehensive comparison report.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from project_analyzer import analyze_project

def extract_zip(zip_path: Path, extract_dir: Path) -> bool:
    """Extract ZIP file to directory."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)
        return True
    except Exception as e:
        print(f"  ❌ Error extracting: {e}")
        return False

def analyze_zip_project(zip_path: Path, temp_dir: Path) -> Dict[str, Any]:
    """Analyze a single project from ZIP."""
    print(f"\n📦 Analyzing: {zip_path.name}")
    
    # Create unique extraction directory
    project_name = zip_path.stem.split('-')[0]  # Extract project name from ZIP
    extract_path = temp_dir / project_name
    
    # Clean if exists
    if extract_path.exists():
        shutil.rmtree(extract_path)
    
    extract_path.mkdir(parents=True, exist_ok=True)
    
    # Extract ZIP
    if not extract_zip(zip_path, extract_path):
        return {'zip_name': zip_path.name, 'error': 'Extraction failed'}
    
    # Find actual project root (might be nested)
    project_root = extract_path
    contents = list(extract_path.iterdir())
    
    # If single nested directory, go into it
    if len(contents) == 1 and contents[0].is_dir():
        project_root = contents[0]
    
    # Analyze project
    try:
        result = analyze_project(str(project_root), project_name=project_name)
        
        # Add ZIP metadata
        result['zip_name'] = zip_path.name
        result['zip_size_mb'] = round(zip_path.stat().st_size / (1024*1024), 2)
        
        # Calculate documentation score
        total_issues = len(result.get('issues', []))
        total_elements = result.get('stats', {}).get('total_elements', 1)
        score = 100 * (1 - total_issues / max(total_elements, 1)) if total_elements > 0 else 0
        result['documentation_score'] = round(score, 1)
        
        print(f"  ✅ {project_name}: {result['documentation_score']}% - {total_issues} issues in {total_elements} elements")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Analysis error: {e}")
        return {'zip_name': zip_path.name, 'error': str(e)}

def main():
    """Main function."""
    # Python ZIPs to analyze
    python_projects = [
        'aiohttp-0.20.0.zip',
        'cpython-2.7.zip',
        'django-main.zip',
        'django-stable-1.8.x.zip',
        'example_project.zip',
        'fastapi-fastapi-0.128.0-12-g47391ea.zip',
        'flask-main.zip',
        'httpx-master.zip',
        'langchain-master.zip',
        'pandas-main.zip',
        'psf-requests-v2.32.5-7-g7029833.zip',
        'rich-master.zip',
        'scikit-learn-main.zip',
        'synthcity-main.zip',
        'youtube-dl-2015.01.23.zip',
        'youtube-dl-master.zip',
    ]
    
    print("=" * 100)
    print("DOCUMENTATION CONSISTENCY - ALL PYTHON PROJECTS ANALYSIS")
    print("=" * 100)
    
    # Create temp directory
    temp_dir = Path('/tmp/analysis_temp')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    current_dir = Path('.')
    
    for project_zip in python_projects:
        zip_path = current_dir / project_zip
        
        if not zip_path.exists():
            print(f"\n⚠️  Skipping: {project_zip} (not found)")
            continue
        
        result = analyze_zip_project(zip_path, temp_dir)
        results.append(result)
    
    # Clean up temp
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Generate report
    print("\n" + "=" * 100)
    print("ANALYSIS SUMMARY")
    print("=" * 100)
    print()
    
    # Sort by documentation score
    sorted_results = sorted(
        [r for r in results if 'error' not in r],
        key=lambda x: x.get('documentation_score', 0),
        reverse=True
    )
    
    # Table header
    print(f"{'Rank':<5} {'Project':<35} {'Score':<8} {'Size':<8} {'Elements':<10} {'Issues':<10} {'Languages':<30}")
    print("-" * 106)
    
    for rank, result in enumerate(sorted_results, 1):
        project_name = result.get('zip_name', 'unknown').replace('.zip', '')[:32]
        score = result.get('documentation_score', 0)
        size = f"{result.get('zip_size_mb', 0)}MB"
        elements = result.get('stats', {}).get('total_elements', 0)
        issues = len(result.get('issues', []))
        langs = ', '.join(result.get('languages', []))[:28]
        
        # Color coding
        if score >= 95:
            status = "🟢"
        elif score >= 90:
            status = "🟡"
        else:
            status = "🔴"
        
        print(f"{rank:<5} {project_name:<35} {status} {score:<6}% {size:<8} {elements:<10} {issues:<10} {langs:<30}")
    
    print()
    
    # Errors
    errors = [r for r in results if 'error' in r]
    if errors:
        print(f"\n⚠️  Analysis Errors ({len(errors)}):")
        for result in errors:
            print(f"  • {result['zip_name']}: {result.get('error', 'Unknown error')}")
    
    # Statistics
    print("\n" + "=" * 100)
    print("DETAILED STATISTICS")
    print("=" * 100)
    print()
    
    successful = [r for r in results if 'error' not in r]
    
    if successful:
        scores = [r.get('documentation_score', 0) for r in successful]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        total_elements = sum(r.get('stats', {}).get('total_elements', 0) for r in successful)
        total_issues = sum(len(r.get('issues', [])) for r in successful)
        
        print(f"Total projects analyzed: {len(successful)}")
        print(f"Average documentation score: {avg_score:.1f}%")
        print(f"Total code elements: {total_elements:,}")
        print(f"Total documentation issues: {total_issues:,}")
        print()
        
        # Issues breakdown
        print("Issues by type (total across all projects):")
        issues_by_type = {
            'MISSING_DOC_CLASS': 0,
            'MISSING_DOC_METHOD': 0,
            'MISSING_DOC_FUNCTION': 0,
            'INCONSISTENCY_PARAM': 0,
        }
        
        for result in successful:
            for issue_type, count in result.get('issues_by_type', {}).items():
                if issue_type in issues_by_type:
                    issues_by_type[issue_type] += count
        
        for issue_type, count in sorted(issues_by_type.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  • {issue_type}: {count}")
        
        print()
        
        # Language distribution
        print("Language distribution:")
        lang_stats = {}
        for result in successful:
            for lang in result.get('languages', []):
                lang_stats[lang] = lang_stats.get(lang, 0) + 1
        
        for lang, count in sorted(lang_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {lang}: {count} projects")
    
    # Save results to JSON
    output_file = Path('analysis_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to: {output_file}")
    print("=" * 100)

if __name__ == '__main__':
    main()
