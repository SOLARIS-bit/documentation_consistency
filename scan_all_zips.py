#!/usr/bin/env python3
"""
Scan all ZIP files in the current directory and detect languages.
"""

import zipfile
from pathlib import Path
from collections import defaultdict
import json

# Language extensions mapping
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.java': 'Java',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.go': 'Go',
    '.rs': 'Rust',
    '.c': 'C',
    '.h': 'C/C++',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.hpp': 'C++',
    '.cs': 'C#',
    '.php': 'PHP',
    '.rb': 'Ruby',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.r': 'R',
    '.m': 'Objective-C',
    '.swift': 'Swift',
    '.sh': 'Bash',
}

def scan_zip(zip_path: Path) -> dict:
    """Scan a ZIP file and detect languages."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            
            # Count files by extension
            extensions = defaultdict(int)
            languages = defaultdict(int)
            total_files = 0
            
            for filename in file_list:
                if filename.endswith('/'):  # Skip directories
                    continue
                
                total_files += 1
                ext = Path(filename).suffix.lower()
                
                if ext:
                    extensions[ext] += 1
                    if ext in LANGUAGE_EXTENSIONS:
                        lang = LANGUAGE_EXTENSIONS[ext]
                        languages[lang] += 1
            
            return {
                'zip_name': zip_path.name,
                'size_mb': round(zip_path.stat().st_size / (1024*1024), 2),
                'total_files': total_files,
                'code_files': sum(languages.values()),
                'languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)),
                'top_extensions': dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]),
            }
    except Exception as e:
        return {
            'zip_name': zip_path.name,
            'error': str(e)
        }

def main():
    """Main function."""
    zip_dir = Path('.')
    zip_files = sorted(zip_dir.glob('*.zip'))
    
    print("=" * 100)
    print("LANGUAGE DETECTION REPORT - ALL ZIP FILES")
    print("=" * 100)
    print()
    
    results = []
    for zip_path in zip_files:
        result = scan_zip(zip_path)
        results.append(result)
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['zip_name']}")
        print(f"   Size: {result['size_mb']} MB")
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   Total files: {result['total_files']}")
            print(f"   Code files: {result['code_files']}")
            
            if result['languages']:
                print(f"   Languages detected:")
                for lang, count in result['languages'].items():
                    print(f"     • {lang}: {count} files")
            else:
                print(f"   ⚠️  No code files detected")
        
        print()
    
    # Summary table
    print("=" * 100)
    print("SUMMARY TABLE")
    print("=" * 100)
    print()
    
    print(f"{'ZIP File':<40} {'Size':<10} {'Files':<8} {'Code':<6} {'Languages':<40}")
    print("-" * 104)
    
    for result in results:
        if 'error' in result:
            print(f"{result['zip_name']:<40} {'N/A':<10} {'ERROR':<8} {'-':<6} {'-':<40}")
        else:
            langs = ', '.join(result['languages'].keys()) if result['languages'] else 'None'
            if len(langs) > 38:
                langs = langs[:35] + '...'
            
            print(f"{result['zip_name']:<40} {str(result['size_mb']) + 'MB':<10} {result['total_files']:<8} {result['code_files']:<6} {langs:<40}")
    
    print()
    
    # Language statistics
    print("=" * 100)
    print("LANGUAGE STATISTICS")
    print("=" * 100)
    print()
    
    all_languages = defaultdict(int)
    for result in results:
        if 'languages' in result:
            for lang, count in result['languages'].items():
                all_languages[lang] += count
    
    if all_languages:
        print("Total code files by language:")
        for lang, count in sorted(all_languages.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {lang}: {count} files")
    
    print()
    print("=" * 100)

if __name__ == '__main__':
    main()
