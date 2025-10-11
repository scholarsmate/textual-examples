# GitHub Actions Workflows

This directory contains CI/CD workflows for the Textual TUI Apps project.

## Workflows

### 🚀 release.yml - Build and Release Packages

**Triggers:** When a version tag is pushed (e.g., `v1.0.2`)

**Purpose:** Automatically builds both packages and creates a GitHub Release with distribution files.

**Outputs:**

- GitHub Release with wheel and source distribution files
- Artifacts available for download from Actions tab

### 🧪 build-test.yml - Build and Test

**Triggers:** On push to `main` or pull requests

**Purpose:** Tests that packages build correctly across multiple platforms and Python versions.

**Test Matrix:**

- OS: Ubuntu, Windows, macOS
- Python: 3.10, 3.11, 3.12, 3.13

## Usage

### Creating a Release

1. Update version in `VERSION` and both `pyproject.toml` files
2. Commit and push to main
3. Create and push a version tag:

   ```bash
   git tag v1.0.2
   git push origin v1.0.2
   ```

4. GitHub Actions will automatically build and release

### Version Bumping with Hatch

```bash
# Choose one bump type
hatch version patch   # X.Y.(Z+1)
hatch version minor   # X.(Y+1).0
hatch version major   # (X+1).0.0

# Tag and push
git add VERSION
git commit -m "Bump version to $(cat VERSION)"
git tag v$(cat VERSION)
git push origin main
git push origin v$(cat VERSION)
```

## Artifacts

Build artifacts are available:

- **From Actions tab:** Download `task-app-dist` or `budget-app-dist`
- **From Releases page:** Download individual `.whl` or `.tar.gz` files

## Configuration

See [CI-CD-SETUP.md](../CI-CD-SETUP.md) for detailed documentation.
