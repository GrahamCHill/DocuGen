import subprocess
import sys
import os
import shutil

ICON_WIN = 'assets/icon.ico'
ICON_MAC = 'assets/icon.icns'


def build():
    print("Building DocuGen GUI application...")
    
    # Get the project root directory (one level up from this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Entry point is src/docugen/main.py
    # We want to bundle it as a single windowed application
    
    entry_point = os.path.join(project_root, "src", "docugen", "main.py")
    
    if not os.path.exists(entry_point):
        print(f"Error: Could not find entry point at {entry_point}")
        sys.exit(1)

    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing it...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Determine which icon to use
    if sys.platform == "win32":
        icon_path = os.path.join(script_dir, ICON_WIN)
    elif sys.platform == "darwin":
        icon_path = os.path.join(script_dir, ICON_MAC)
    else:
        icon_path = None

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "DocuGen",
        "--add-data", f"{os.path.join(project_root, 'src', 'docugen')}{os.pathsep}docugen",
    ]

    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    cmd.append(entry_point)

    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful!")
        print("The executable can be found in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
