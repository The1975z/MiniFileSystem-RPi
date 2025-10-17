import sys
import os

print("Starting FILE-MANAGEMENT-SYSTEM-OS...")
print("Checking dependencies...\n")

try:
    import check_deps
    if not check_deps.check_and_install_dependencies():
        print("\n❌ Dependency check failed. Please install required packages.")
        input("\nPress Enter to exit...")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error checking dependencies: {e}")
    input("\nPress Enter to exit...")
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main_integrated import main
    main()
except Exception as e:
    print(f"\n❌ Error starting application: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)
