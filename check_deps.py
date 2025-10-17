import subprocess
import sys
import os


def check_and_install_dependencies():
    print("=" * 60)
    print("FILE-MANAGEMENT-SYSTEM-OS - Dependency Checker")
    print("=" * 60)

    required_packages = {
        'paramiko': 'paramiko>=3.0.0',
        'customtkinter': 'customtkinter>=5.0.0',
        'darkdetect': 'darkdetect~=0.3.1',
        'typing_extensions': 'typing-extensions~=4.4.0',
        'packaging': 'packaging'
    }

    missing_packages = []
    installed_packages = []

    print("\nChecking dependencies...")
    print("-" * 60)

    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {package:20s} - Already installed")
            installed_packages.append(package)
        except ImportError:
            print(f"✗ {package:20s} - Missing")
            missing_packages.append(pip_name)

    print("-" * 60)

    if not missing_packages:
        print("\n✓ All dependencies are installed!")
        print("=" * 60)
        return True

    print(f"\n⚠ Found {len(missing_packages)} missing package(s)")
    print("\nMissing packages:")
    for pkg in missing_packages:
        print(f"  - {pkg}")

    print("\nDo you want to install missing packages now? (y/n): ", end="")
    response = input().strip().lower()

    if response != 'y':
        print("\n❌ Installation cancelled.")
        print("Please install manually using:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("=" * 60)
        return False

    print("\n📦 Installing missing packages...")
    print("-" * 60)

    for package in missing_packages:
        try:
            print(f"\nInstalling {package}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✓ Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}")
            print(f"   Error: {e}")
            return False

    print("-" * 60)
    print("\n✓ All dependencies installed successfully!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = check_and_install_dependencies()
    if not success:
        sys.exit(1)
