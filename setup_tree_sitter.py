#!/usr/bin/env python3
"""
Setup script to install tree-sitter language libraries.
Supports: Python, Java, C, C++, Go, JavaScript, TypeScript, Rust, C#, Ruby, PHP
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd: list, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"   Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - Command not found: {cmd[0]}")
        return False

def install_tree_sitter_libs():
    """Install tree-sitter language libraries."""
    print("\n🌳 Tree-Sitter Language Setup\n")
    
    # Check if tree-sitter is installed
    try:
        import tree_sitter
        print(f"✅ tree-sitter is installed (version: {tree_sitter.__version__ if hasattr(tree_sitter, '__version__') else 'unknown'})")
    except ImportError:
        print("❌ tree-sitter is not installed. Install with:")
        print("   pip install tree-sitter>=0.20.0")
        return False

    system = platform.system()
    languages = {
        'python': 'tree-sitter-python',
        'java': 'tree-sitter-java',
        'c': 'tree-sitter-c',
        'cpp': 'tree-sitter-cpp',
        'go': 'tree-sitter-go',
        'javascript': 'tree-sitter-javascript',
        'typescript': 'tree-sitter-typescript',
        'rust': 'tree-sitter-rust',
        'c_sharp': 'tree-sitter-c-sharp',
        'ruby': 'tree-sitter-ruby',
        'php': 'tree-sitter-php',
    }

    print(f"System: {system}")
    print(f"Python: {sys.version.split()[0]}\n")
    
    success_count = 0
    
    if system == "Linux":
        print("📝 Installing language bindings for Linux...\n")
        
        # Install build essentials if needed
        if run_command(["which", "gcc"], "Checking for GCC"):
            pass
        else:
            print("⚠️  GCC not found. Install build essentials:")
            print("   Ubuntu/Debian: sudo apt-get install build-essential")
            print("   Fedora: sudo dnf install gcc g++ make")
    
    elif system == "Darwin":
        print("📝 Installing language bindings for macOS...\n")
        print("⚠️  Ensure you have Xcode Command Line Tools installed:")
        print("   xcode-select --install\n")
    
    # Install language bindings via pip
    for lang_name, package_name in languages.items():
        if run_command([sys.executable, "-m", "pip", "install", package_name], 
                      f"Installing {lang_name} support"):
            success_count += 1
    
    print(f"\n✅ Successfully installed {success_count}/{len(languages)} language bindings")
    
    if success_count < len(languages):
        print("\n⚠️  Some language bindings failed to install.")
        print("   The analyzer will still work but may have limited language support.")
    
    print("\n📖 Supported languages are now available for analysis:")
    for lang in sorted(languages.keys()):
        print(f"   • {lang}")
    
    return success_count > 0

def main():
    print("=" * 60)
    print("Tree-Sitter Language Libraries Setup")
    print("=" * 60)
    
    try:
        install_tree_sitter_libs()
        print("\n🎉 Setup complete!")
        print("\nYou can now analyze projects with multiple programming languages.")
        print("Run: streamlit run app.py")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
