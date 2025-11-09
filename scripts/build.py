#!/usr/bin/env python3
"""
Build script for DAM SDK package
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command"""
    print(f"🚀 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode

def main():
    """Build and package the SDK"""
    project_root = Path(__file__).parent.parent
    
    print("🏗️  Building DAM Python SDK...")
    print("=" * 50)
    
    # Clean previous builds
    print("\n1. Cleaning previous builds...")
    run_command("rm -rf build/ dist/ *.egg-info", check=False)
    
    # Run tests
    print("\n2. Running tests...")
    os.chdir(project_root)
    test_result = run_command("python -m pytest tests/ -v", check=False)
    if test_result != 0:
        print("❌ Tests failed! Aborting build.")
        sys.exit(1)
    print("✅ Tests passed!")
    
    # Build package
    print("\n3. Building package...")
    build_result = run_command("python setup.py sdist bdist_wheel", check=False)
    if build_result != 0:
        print("❌ Build failed!")
        sys.exit(1)
    print("✅ Package built successfully!")
    
    # List built packages
    print("\n4. Built packages:")
    run_command("ls -la dist/", check=False)
    
    # Check package
    print("\n5. Checking package...")
    check_result = run_command("twine check dist/*", check=False)
    if check_result == 0:
        print("✅ Package check passed!")
    else:
        print("⚠️  Package check warnings (install twine: pip install twine)")
    
    print("\n🎉 Build completed!")
    print("\nTo install locally:")
    print("  pip install dist/dam_sdk_py-1.0.0-py3-none-any.whl")
    print("\nOr from current directory:")
    print("  pip install .")
    print("\nOr from GitHub:")
    print("  pip install git+https://github.com/aubreyosenda/dam_sdk_py.git")

if __name__ == "__main__":
    main()