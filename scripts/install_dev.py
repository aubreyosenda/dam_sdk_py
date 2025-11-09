#!/usr/bin/env python3
"""
Development installation script for DAM SDK
Installs the package in development mode with all dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    print(f"   Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stderr:
            print(f"   Error output: {e.stderr}")
        return False

def main():
    """Main installation script"""
    project_root = Path(__file__).parent.parent
    
    print("🚀 DAM SDK Development Installation")
    print("=" * 50)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"🐍 Python version: {python_version}")
    
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    # Change to project directory
    os.chdir(project_root)
    print(f"📁 Working directory: {project_root}")
    
    # Create virtual environment (optional)
    create_venv = input("Create virtual environment? (y/n): ").lower().strip()
    if create_venv in ['y', 'yes']:
        venv_name = input("Virtual environment name (default: venv): ") or "venv"
        
        if not run_command(f"python -m venv {venv_name}", "Creating virtual environment"):
            print("❌ Failed to create virtual environment")
            sys.exit(1)
        
        # Determine activation command
        if sys.platform == "win32":
            activate_cmd = f"{venv_name}\\Scripts\\activate"
            pip_cmd = f"{venv_name}\\Scripts\\pip"
        else:
            activate_cmd = f"source {venv_name}/bin/activate"
            pip_cmd = f"{venv_name}/bin/pip"
        
        print(f"🔧 Virtual environment created: {venv_name}")
        print(f"💡 Activate with: {activate_cmd}")
    else:
        pip_cmd = "pip"
    
    # Install the package in development mode
    print("\n📦 Installing DAM SDK...")
    
    # Install base package
    if not run_command(f"{pip_cmd} install -e .", "Installing base package"):
        print("❌ Failed to install base package")
        sys.exit(1)
    
    # Install development dependencies
    install_dev = input("Install development dependencies? (y/n): ").lower().strip()
    if install_dev in ['y', 'yes']:
        if not run_command(f"{pip_cmd} install -e \".[dev]\"", "Installing development dependencies"):
            print("⚠️  Failed to install some development dependencies")
    
    # Install async dependencies
    install_async = input("Install async dependencies? (y/n): ").lower().strip()
    if install_async in ['y', 'yes']:
        if not run_command(f"{pip_cmd} install -e \".[async]\"", "Installing async dependencies"):
            print("⚠️  Failed to install async dependencies")
    
    # Run tests
    run_tests = input("Run tests? (y/n): ").lower().strip()
    if run_tests in ['y', 'yes']:
        if not run_command(f"{pip_cmd} install pytest", "Installing pytest"):
            print("⚠️  Failed to install pytest")
        else:
            if not run_command("python -m pytest tests/ -v", "Running tests"):
                print("⚠️  Some tests failed")
            else:
                print("✅ All tests passed!")
    
    # Verify installation
    print("\n🔍 Verifying installation...")
    verify_script = """
try:
    from dam_sdk import DAMClient, AsyncDAMClient, __version__
    print(f"✅ DAM SDK imported successfully! Version: {__version__}")
    
    # Test basic functionality
    client = DAMClient(
        api_url='http://localhost:55055',
        key_id='test',
        key_secret='test'
    )
    print("✅ Client creation successful!")
    print("🎉 Installation completed successfully!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Verification failed: {e}")
"""
    
    result = subprocess.run([sys.executable, "-c", verify_script], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"⚠️  Verification warnings: {result.stderr}")
    
    # Final instructions
    print("\n📚 Next Steps:")
    print("1. Check out the examples in the 'examples/' directory")
    print("2. Run: python examples/basic_usage.py")
    print("3. Read the documentation in README.md")
    print("4. Explore framework examples in examples/web_framework_examples/")
    
    print("\n🎉 Development environment ready!")

if __name__ == "__main__":
    main()