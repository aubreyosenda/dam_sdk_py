#!/usr/bin/env python3
"""
Check if project is ready for packaging
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Verify the project structure is clean"""
    project_root = Path(__file__).parent
    
    # Files that should NOT exist
    forbidden_dirs = ['venv', 'env', '.venv', 'build', 'dist']
    forbidden_files = ['.env', '*.egg-info']
    
    print("🔍 Checking project structure...")
    
    # Check for virtual environments
    for dir_name in forbidden_dirs:
        if (project_root / dir_name).exists():
            print(f"❌ Found {dir_name}/ - Remove before packaging!")
            return False
    
    # Check for required files
    required_files = ['setup.py', 'pyproject.toml', 'README.md', 'LICENSE']
    for file_name in required_files:
        if not (project_root / file_name).exists():
            print(f"❌ Missing {file_name} - Required for packaging!")
            return False
    
    # Check for package directory
    if not (project_root / 'dam_sdk').exists():
        print("❌ Missing dam_sdk/ package directory!")
        return False
    
    print("✅ Project structure is clean!")
    return True

def check_package_content():
    """Verify package content is complete"""
    package_dir = Path(__file__).parent / 'dam_sdk'
    
    required_modules = [
        '__init__.py',
        'client.py', 
        'async_client.py',
        'models.py',
        'exceptions.py',
        'utils.py',
        'constants.py'
    ]
    
    print("\n🔍 Checking package content...")
    
    for module in required_modules:
        if not (package_dir / module).exists():
            print(f"❌ Missing dam_sdk/{module}")
            return False
    
    # Check __init__.py exports
    init_file = package_dir / '__init__.py'
    with open(init_file, 'r') as f:
        content = f.read()
    
    required_exports = ['DAMClient', 'AsyncDAMClient', '__version__']
    for export in required_exports:
        if export not in content:
            print(f"❌ Missing export in __init__.py: {export}")
            return False
    
    print("✅ Package content is complete!")
    return True

def check_can_import():
    """Verify the package can be imported"""
    print("\n🔍 Testing package import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from sdks.python.dam_sdk_py.dam_sdk._init_ import DAMClient, AsyncDAMClient, __version__
        print(f"✅ Package imports successfully! Version: {__version__}")
        
        # Test client creation
        client = DAMClient(
            api_url='http://test.com',
            key_id='test',
            key_secret='test'
        )
        print("✅ Client creation works!")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Run all checks"""
    print("🚀 DAM SDK Packaging Pre-Flight Check")
    print("=" * 50)
    
    checks = [
        check_directory_structure,
        check_package_content, 
        check_can_import
    ]
    
    all_passed = all(check() for check in checks)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Ready for packaging.")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Ready for v1.0.0 release'") 
        print("3. git push origin main")
        print("4. python -m build")
        print("5. twine upload dist/*")
    else:
        print("❌ Some checks failed. Fix issues before packaging.")
        sys.exit(1)

if __name__ == "__main__":
    main()