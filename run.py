import sys
import subprocess
import importlib.util
import os
from pathlib import Path

REQUIRED_PACKAGES = {
    'darkdetect': 'darkdetect~=0.3.1',
    'typing_extensions': 'typing-extensions~=4.4.0',
    'packaging': 'packaging',
    'paramiko': 'paramiko>=3.0.0',
    'customtkinter': 'customtkinter>=5.0.0'
}

def check_package_installed(package_name):
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(pip_package_spec):
    try:
        print(f"Installing {pip_package_spec}...")
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', pip_package_spec],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.STDOUT
        )
        return True
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--user', pip_package_spec],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.STDOUT
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {pip_package_spec}: {e}")
            return False

def upgrade_pip():
    try:
        print("Upgrading pip...")
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.STDOUT
        )
        print("Pip upgraded successfully")
    except:
        print("Could not upgrade pip (may require admin rights)")

def check_and_install_dependencies():
    print("=" * 60)
    print("Checking required dependencies...")
    print("=" * 60)
    
    missing_packages = []
    
    for import_name, pip_spec in REQUIRED_PACKAGES.items():
        package_name = pip_spec.split('[')[0].split('~')[0].split('>')[0].split('=')[0]
        
        if check_package_installed(import_name):
            print(f"{package_name} - installed")
        else:
            print(f"{package_name} - not installed")
            missing_packages.append((import_name, pip_spec, package_name))
    
    if missing_packages:
        print("\n" + "=" * 60)
        print(f"Found {len(missing_packages)} packages to install")
        print("=" * 60)
        
        upgrade_pip()
        
        print("\nInstalling missing packages...\n")
        
        failed_packages = []
        for import_name, pip_spec, display_name in missing_packages:
            if install_package(pip_spec):
                print(f"Installed {display_name} successfully")
            else:
                failed_packages.append(display_name)
        
        print("\n" + "=" * 60)
        
        if failed_packages:
            print("Installation incomplete!")
            print(f"Failed to install: {', '.join(failed_packages)}")
            print("\nTry:")
            print("1. Run as Administrator/sudo")
            print("2. Manual install: pip install -r requirements.txt")
            print("=" * 60)
            return False
        else:
            print("All packages installed successfully!")
            print("=" * 60)
    else:
        print("\nAll dependencies satisfied")
        print("=" * 60)
    
    return True

def run_main_application():
    try:
        src_path = Path(__file__).parent / 'src'
        if src_path.exists():
            sys.path.insert(0, str(src_path))
        
        print("\nStarting GUI-OS Application...\n")
        print("=" * 60)
        
        from src.main import main
        main()
        
    except ImportError as e:
        print(f"\nCannot load application: {e}")
        print("Check that src/main.py exists with main() function")
        return False
    except Exception as e:
        print(f"\nApplication error: {e}")
        return False
    
    return True

def main():
    print("\n" + "GUI-OS Application Launcher".center(60))
    print("=" * 60)
    print("Version: 1.0.0")
    print(f"Python: {sys.version}")
    print("=" * 60)
    
    if sys.version_info < (3, 6):
        print("Python 3.6 or higher required")
        print(f"Current Python: {sys.version}")
        sys.exit(1)
    
    if not check_and_install_dependencies():
        print("\nPlease fix dependency issues before running")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    if not run_main_application():
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)