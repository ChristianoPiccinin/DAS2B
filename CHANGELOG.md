# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-06-19

### Added

- **CI/CD Pipeline Infrastructure**
  - PR validation workflow (ruff linting, mypy type checking, pytest unit tests)
  - Automated dev deployment workflow on main branch merges
  - Manual staging deployment workflow with health checks
  - Release-based production deployment workflow
  - Python dependency caching for faster builds
  - Health check module with retry logic for deployment verification
  - Code quality enforcement with ruff and mypy
  - Test coverage reporting and HTML artifacts
  - Comprehensive CI/CD guide documentation

### Changed

- Updated README with CI/CD pipeline overview and quick-start instructions
- Project configuration now includes `pyproject.toml` with tool settings for ruff, mypy, and pytest

### Details

The CI/CD improvements establish a robust pipeline for code quality, testing, and multi-environment deployments:

1. **PR Validation**: All pull requests to main must pass linting, type checking, and unit tests before merge
2. **Dev Deployment**: Automatic, immediate deployment to dev environment on code merge
3. **Staging Deployment**: Manual, on-demand deployment to staging for pre-production validation
4. **Production Deployment**: Explicit, release-based deployment via GitHub Releases for production safety

See `docs/ci-cd-guide.md` for detailed usage instructions.
