#!/usr/bin/env python3
"""
Version Bump Script for Textual TUI Apps

Updates the VERSION file and optionally creates a git tag.
The build_packages.py script reads this file to set package versions.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_current_version(version_file: Path) -> str:
    """Read current version from VERSION file."""
    if not version_file.exists():
        print(f"❌ VERSION file not found at {version_file}")
        sys.exit(1)
    return version_file.read_text().strip()


def update_version_file(version_file: Path, new_version: str) -> None:
    """Update VERSION file."""
    version_file.write_text(f"{new_version}\n")
    print(f"✅ Updated {version_file}")


def validate_version(version: str) -> bool:
    """Validate semantic version format."""
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def run_git_command(args: list[str]) -> bool:
    """Run a git command and return success status."""
    try:
        subprocess.run(["git"] + args, check=True, capture_output=True, text=True)
        print(f"✅ git {' '.join(args)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ git {' '.join(args)} failed:")
        print(e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Bump version for Textual TUI Apps")
    parser.add_argument("version", help="New version number (e.g., 1.2.0)")
    parser.add_argument("--no-commit", action="store_true", help="Don't create git commit")
    parser.add_argument("--no-tag", action="store_true", help="Don't create git tag")
    parser.add_argument("--push", action="store_true", help="Push commit and tag to origin")

    args = parser.parse_args()
    new_version = args.version

    # Validate version format
    if not validate_version(new_version):
        print(f"❌ Invalid version format: {new_version}")
        print("Version must be in format: MAJOR.MINOR.PATCH (e.g., 1.2.0)")
        sys.exit(1)

    # Get repository root
    repo_root = Path(__file__).parent

    # Show current version
    version_file = repo_root / "VERSION"
    current_version = get_current_version(version_file)
    print(f"\n📦 Current version: {current_version}")
    print(f"📦 New version: {new_version}\n")

    # Confirm
    response = input("Continue? [y/N]: ")
    if response.lower() != "y":
        print("Aborted.")
        sys.exit(0)

    print("\n🔄 Updating version file...\n")

    # Update VERSION file
    update_version_file(version_file, new_version)

    print("\n✅ VERSION file updated!\n")
    print("ℹ️  Note: build_packages.py will use this version when building packages.\n")

    # Git operations
    if not args.no_commit:
        print("🔄 Creating git commit...\n")

        if not run_git_command(["add", "VERSION"]):
            sys.exit(1)

        commit_msg = f"Bump version to {new_version}"
        if not run_git_command(["commit", "-m", commit_msg]):
            sys.exit(1)

        print()

        if not args.no_tag:
            print("🔄 Creating git tag...\n")
            tag_name = f"v{new_version}"
            if not run_git_command(["tag", tag_name]):
                sys.exit(1)
            print()

            if args.push:
                print("🔄 Pushing to origin...\n")
                if not run_git_command(["push", "origin", "main"]):
                    sys.exit(1)
                if not run_git_command(["push", "origin", tag_name]):
                    sys.exit(1)
                print("\n✅ Pushed commit and tag to origin!")
                print(f"\n🚀 GitHub Actions will now build and release version {new_version}")
            else:
                print("ℹ️  To push the changes, run:")
                print("   git push origin main")
                print(f"   git push origin v{new_version}")
        else:
            print("ℹ️  Tag creation skipped.")
    else:
        print("ℹ️  Git commit skipped.")
        print("\nTo commit manually:")
        print("   git add VERSION")
        print(f"   git commit -m 'Bump version to {new_version}'")
        print(f"   git tag v{new_version}")
        print("   git push origin main")
        print(f"   git push origin v{new_version}")

    print(f"\n✅ Version bump to {new_version} complete!")


if __name__ == "__main__":
    main()
