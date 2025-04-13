#!/usr/bin/env python3
"""
Build script to create a standalone executable for ServerInspect using PyInstaller.
Supports cross-platform builds for Windows, macOS, and Linux.
"""

import os
import platform
import subprocess
import sys
import argparse
import shutil
from pathlib import Path


def get_platform_info(target_platform=None):
    """Get detailed platform information."""
    if target_platform:
        system = target_platform
    else:
        system = platform.system().lower()

    machine = platform.machine().lower()

    return {
        "system": system,
        "machine": machine,
        "is_windows": system == "windows",
        "is_macos": system == "macos" or system == "darwin",
        "is_linux": system == "linux",
    }


def build_executable(target_platform=None):
    """Build the executable using PyInstaller."""
    platform_info = get_platform_info(target_platform)
    print(f"Building for {platform_info['system']} ({platform_info['machine']})...")

    try:
        # Ensure output directory exists
        dist_dir = Path("dist")
        if not dist_dir.exists():
            dist_dir.mkdir(parents=True)

        # Clean existing build directories if they exist
        if platform_info["is_windows"]:
            clean_dir = dist_dir / "serverinspect"
        elif platform_info["is_macos"]:
            clean_dir = dist_dir / "serverinspect-macos"
        else:  # Linux
            clean_dir = dist_dir / "serverinspect-linux"

        if clean_dir.exists():
            print(f"Cleaning existing directory: {clean_dir}")
            shutil.rmtree(clean_dir)

        # Build command with platform-specific options
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "-y", "--onefile"]

        # Add platform-specific options
        if platform_info["is_windows"]:
            cmd.append("--name=serverinspect")
        elif platform_info["is_macos"]:
            cmd.append("--name=serverinspect-macos")
        else:  # Linux
            cmd.append("--name=serverinspect-linux")

        # Always use src layout
        cmd.extend(
            ["--add-data", f"src/serverinspect/templates:templates", "src/main.py"]
        )

        # Run PyInstaller
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Output build log
        if result.stdout:
            print(result.stdout)

        # Create platform-specific output
        create_platform_output(platform_info, dist_dir)

    except subprocess.CalledProcessError as e:
        print("Error during build:")
        if e.stderr:
            print(e.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1

    return 0


def create_platform_output(platform_info, dist_dir):
    """Create platform-specific output files."""
    # In onefile mode, the executable is directly in the dist directory
    if platform_info["is_windows"]:
        exe_path = dist_dir / "serverinspect.exe"
        output_name = f"serverinspect-windows-{platform_info['machine']}.exe"
    elif platform_info["is_macos"]:
        exe_path = dist_dir / "serverinspect-macos"
        output_name = f"serverinspect-macos-{platform_info['machine']}"
    else:  # Linux
        exe_path = dist_dir / "serverinspect-linux"
        output_name = f"serverinspect-linux-{platform_info['machine']}"

    # Check if the executable was created
    if not exe_path.exists():
        print(f"Build did not produce expected executable at {exe_path}")
        print("Checking for alternative locations...")

        # Look for alternatives
        for path in dist_dir.glob("*serverinspect*"):
            if path.is_file() and (os.access(path, os.X_OK) or path.suffix == ".exe"):
                exe_path = path
                print(f"Found executable at: {exe_path}")
                break
        else:
            print("No executable found. Build may have failed.")
            return

    # Create the output file
    output_path = dist_dir / output_name
    shutil.copy2(exe_path, output_path)

    # Make the file executable on Unix-like systems
    if not platform_info["is_windows"]:
        os.chmod(output_path, 0o755)

    print(f"\nBuild successful! Executable created at: {output_path}")
    print(f"\nYou can now distribute this executable file.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build ServerInspect executable")
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "macos"],
        help="Target platform for the build",
    )
    args = parser.parse_args()

    print("Building ServerInspect executable...")
    return build_executable(args.platform)


if __name__ == "__main__":
    sys.exit(main())
