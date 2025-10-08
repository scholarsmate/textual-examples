#!/usr/bin/env python3
"""Build script to create self-contained packages without source duplication.

This script:
1. Creates build directories for each package
2. Copies source files (including shared tui_common) to each build dir
3. Copies package-specific pyproject.toml to each build dir
4. Builds wheel and sdist for each package
5. All build/ and dist/ directories are gitignored

Source structure (committed):
  src/
    tui_common/     # Shared library (single copy)
    task_app/       # Task app
    budget_app/     # Budget app

Build structure (NOT committed):
  build/
    task-app/
      tui_common/   # Copy of shared library
      task_app/     # Copy of task app
      pyproject.toml
    budget-app/
      tui_common/   # Copy of shared library
      budget_app/   # Copy of budget app
      pyproject.toml
  dist/
    task-app-*.whl
    budget-app-*.whl
"""

import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs():
    """Remove existing build and dist directories."""
    print("🧹 Cleaning build and dist directories...")
    for dir_name in ["build", "dist"]:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed {dir_name}/")


def copy_tree(src: Path, dst: Path, description: str):
    """Copy a directory tree with progress message."""
    print(f"   Copying {description}...")
    shutil.copytree(src, dst, dirs_exist_ok=True)


def create_task_app_package():
    """Create task-app package in build directory."""
    print("\n📦 Building task-app package...")

    build_dir = Path("build/task-app")
    build_dir.mkdir(parents=True, exist_ok=True)

    # Copy source files
    copy_tree(Path("src/task_app"), build_dir / "task_app", "task_app module")
    copy_tree(Path("src/tui_common"), build_dir / "tui_common", "tui_common library")

    # Copy VERSION file into tui_common so it gets packaged
    shutil.copy("VERSION", build_dir / "tui_common" / "VERSION")
    print("   Copying VERSION to tui_common/")

    # Copy supporting files to build root
    for file in ["README.md", "LICENSE"]:
        if Path(file).exists():
            shutil.copy(file, build_dir)
            print(f"   Copying {file}")

    # Create pyproject.toml for task-app
    pyproject_content = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "textual-task-app"
version = "1.0.0"
description = "Task Management TUI Application"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Scholar's Mate", email = "scholarsmate@users.noreply.github.com"}
]
keywords = ["tui", "textual", "terminal", "task-manager", "todo", "cli"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Office/Business",
    "Topic :: Utilities",
]

dependencies = [
    "textual>=6.2.1",
    "bcrypt>=5.0.0",
    "cryptography>=43.0.3",
    "rich>=14.1.0",
    "platformdirs>=3.0.0",
]

[project.scripts]
task-app = "task_app.main:main"

[project.urls]
Homepage = "https://github.com/scholarsmate/textual-examples"
Repository = "https://github.com/scholarsmate/textual-examples"
Issues = "https://github.com/scholarsmate/textual-examples/issues"

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]

[tool.setuptools.package-data]
tui_common = ["VERSION"]
'''

    (build_dir / "pyproject.toml").write_text(pyproject_content)
    print("   Created pyproject.toml")

    return build_dir


def create_budget_app_package():
    """Create budget-app package in build directory."""
    print("\n📦 Building budget-app package...")

    build_dir = Path("build/budget-app")
    build_dir.mkdir(parents=True, exist_ok=True)

    # Copy source files
    copy_tree(Path("src/budget_app"), build_dir / "budget_app", "budget_app module")
    copy_tree(Path("src/tui_common"), build_dir / "tui_common", "tui_common library")

    # Copy VERSION file into tui_common so it gets packaged
    shutil.copy("VERSION", build_dir / "tui_common" / "VERSION")
    print("   Copying VERSION to tui_common/")

    # Copy supporting files to build root
    for file in ["README.md", "LICENSE"]:
        if Path(file).exists():
            shutil.copy(file, build_dir)
            print(f"   Copying {file}")

    # Create pyproject.toml for budget-app
    pyproject_content = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "textual-budget-app"
version = "1.0.0"
description = "Budget Tracking TUI Application"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Scholar's Mate", email = "scholarsmate@users.noreply.github.com"}
]
keywords = ["tui", "textual", "terminal", "budget-tracker", "finance", "cli"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Office/Business",
    "Topic :: Utilities",
]

dependencies = [
    "textual>=6.2.1",
    "bcrypt>=5.0.0",
    "cryptography>=43.0.3",
    "rich>=14.1.0",
    "platformdirs>=3.0.0",
]

[project.scripts]
budget-app = "budget_app.main:main"

[project.urls]
Homepage = "https://github.com/scholarsmate/textual-examples"
Repository = "https://github.com/scholarsmate/textual-examples"
Issues = "https://github.com/scholarsmate/textual-examples/issues"

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]

[tool.setuptools.package-data]
tui_common = ["VERSION"]
'''

    (build_dir / "pyproject.toml").write_text(pyproject_content)
    print("   Created pyproject.toml")

    return build_dir


def build_package(build_dir: Path, package_name: str):
    """Build a package using python -m build."""
    print(f"\n🔨 Building {package_name} package...")

    result = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", "../../dist"],
        cwd=build_dir,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Build failed for {package_name}:")
        print(result.stderr)
        return False

    print(f"✅ Successfully built {package_name}")
    return True


def main():
    """Main build process."""
    print("=" * 60)
    print("Building Task and Budget App Packages")
    print("=" * 60)

    # Clean previous builds
    clean_build_dirs()

    # Create build directories with copied source
    task_build_dir = create_task_app_package()
    budget_build_dir = create_budget_app_package()

    # Create dist directory
    Path("dist").mkdir(exist_ok=True)

    # Build packages
    success = True
    success &= build_package(task_build_dir, "task-app")
    success &= build_package(budget_build_dir, "budget-app")

    if success:
        print("\n" + "=" * 60)
        print("✅ All packages built successfully!")
        print("=" * 60)
        print("\nBuilt packages:")
        for dist_file in sorted(Path("dist").glob("*")):
            print(f"  - {dist_file.name}")
        return 0
    else:
        print("\n❌ Build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
