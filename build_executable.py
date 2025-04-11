#!/usr/bin/env python3
"""
Build script to create a standalone executable for ServerInspect using PyInstaller.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

def main():
    print("Building ServerInspect executable...")
    
    # Determine the platform
    system = platform.system().lower()
    print(f"Detected platform: {system}")
    
    # Build the executable
    try:
        # Use the spec file
        result = subprocess.run(
            ["pyinstaller", "serverinspect.spec", "--clean"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(result.stdout)
        
        # Determine the executable path
        dist_dir = Path("dist")
        if system == "windows":
            exe_path = dist_dir / "serverinspect.exe"
            exe_name = "serverinspect.exe"
        else:
            exe_path = dist_dir / "serverinspect"
            exe_name = "serverinspect"
        
        if exe_path.exists():
            print(f"\nBuild successful! Executable created at: {exe_path}")
            print(f"\nYou can now distribute the executable from the 'dist' directory.")
            print(f"\nTo use ServerInspect, run: ./{exe_name} [command] [options]")
        else:
            print(f"\nBuild completed, but executable not found at expected location: {exe_path}")
            print("Check the 'dist' directory for the output files.")
        
    except subprocess.CalledProcessError as e:
        print("Error during build:")
        print(e.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())