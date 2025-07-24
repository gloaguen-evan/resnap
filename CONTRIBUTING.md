# Contributing Guide

Thank you for considering contributing to this project!

## 🚧 Contribution Guidelines

- Use a feature branch for each contribution.
- Write clear and meaningful commit messages.
- Add tests if relevant.
- Update documentation if needed (README, comments, docstrings, etc.).

## 🧪 Linting & Testing

Before opening a pull request, please run the following commands:

```bash
uv sync --all-extras --all-groups
```

````shell script
chmod +x scripts/*.sh
./scripts/validate-code.sh
./scripts/run_functional_tests.sh
````

💡Want to skip CI tests for your PR? Just pop #no_test in your commit message!

## 📝 Updating the Changelog

Please update the CHANGELOG.md file in your pull request with a short summary of the changes.

## [Unreleased]
### Added
- What i added in my pull request

### Changed
- What i changed in my pull request

### Changed
- What i fixed in my pull request

## 🔒 Tag Protection
⚠️ Git tags starting with v (e.g. v1.2.3) are protected and can only be pushed by the project maintainer.

This is to prevent unauthorized or accidental PyPI releases via GitHub Actions.

Do not push tags manually — your push will be rejected by GitHub’s ruleset.

## 🚀 Releasing
Version tags (e.g. v1.2.3) are pushed manually by the maintainer after merging.
This automatically triggers the GitHub Actions workflow that publishes the release to PyPI.

Thanks again for helping make this project better!
