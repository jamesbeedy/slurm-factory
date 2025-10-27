
# Contributing to Slurm Factory

We welcome contributions to slurm-factory! This guide covers how to contribute code, documentation, and ideas.

## Quick Start

1. **Fork the repository**: [github.com/vantagecompute/slurm-factory](https://github.com/vantagecompute/slurm-factory)
2. **Clone your fork**: `git clone https://github.com/YOUR-USERNAME/slurm-factory.git`
3. **Create a branch**: `git checkout -b feature/your-feature-name`
4. **Make changes**: Implement your feature or fix
5. **Test changes**: Run tests and verify functionality
6. **Submit PR**: Create a pull request with clear description

## Development Setup

### Prerequisites

- Python 3.11+
- LXD
- UV package manager
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/vantagecompute/slurm-factory.git
cd slurm-factory

# Install development dependencies
uv sync --all-extras

# Install pre-commit hooks
pre-commit install

# Run tests
uv run pytest

# Run type checking
uv run mypy slurm_factory/

# Run linting
uv run ruff check slurm_factory/
```

## Contributing Code

### Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking
- **Pytest** for testing

```bash
# Format code
uv run black slurm_factory/

# Lint code
uv run ruff check slurm_factory/ --fix

# Type check
uv run mypy slurm_factory/
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_builder.py

# Run with coverage
uv run pytest --cov=slurm_factory
```

### Adding Features

1. **Create issue**: Discuss the feature before implementing
2. **Write tests**: Add tests for new functionality
3. **Update docs**: Update documentation for new features
4. **Add changelog**: Update CHANGELOG.md

## Documentation

### Building Docs

```bash
# Install Jekyll (for local preview)
gem install jekyll bundler

# Navigate to docs
cd docs/

# Install dependencies
bundle install

# Serve locally
bundle exec jekyll serve

# View at http://localhost:4000
```

### Documentation Structure

```
docs/
├── _config.yml          # Jekyll configuration
├── _data/project.yml    # Project metadata
├── index.md            # Home page
├── installation.md     # Installation guide
├── architecture.md     # Technical architecture
├── deployment.md       # Deployment guide
├── optimization.md     # Performance optimization
├── api-reference.md    # API documentation
├── troubleshooting.md  # Common issues
├── development.md      # Development guide
├── contributing.md     # This file
└── contact.md          # Contact information
```

## Contribution Types

### Code Contributions

- **Bug fixes**: Fix issues in existing code
- **New features**: Add new functionality
- **Performance improvements**: Optimize existing code
- **Test coverage**: Improve test coverage

### Documentation Contributions

- **Fix typos**: Correct spelling and grammar
- **Improve clarity**: Make documentation clearer
- **Add examples**: Provide usage examples
- **Update guides**: Keep documentation current

### Community Contributions

- **Answer questions**: Help users in discussions
- **Report bugs**: File detailed bug reports
- **Feature requests**: Suggest new features
- **Testing**: Test new releases

## Pull Request Process

### Before Submitting

1. **Check existing PRs**: Avoid duplicate work
2. **Run tests**: Ensure all tests pass
3. **Update docs**: Document changes
4. **Follow conventions**: Use consistent code style

### PR Description

Include:
- **Clear title**: Describe what the PR does
- **Description**: Explain the changes and why
- **Testing**: How you tested the changes
- **Breaking changes**: Note any breaking changes

### Example PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Reporting Issues

### Bug Reports

Include:
- **Environment**: OS, Python version, LXD version
- **Steps to reproduce**: Clear reproduction steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs**: Relevant error messages or logs

### Feature Requests

Include:
- **Use case**: Why you need this feature
- **Proposed solution**: How you think it should work
- **Alternatives**: Other solutions you've considered
- **Examples**: Examples of similar features

## Development Guidelines

### Code Organization

```
slurm_factory/
├── __init__.py         # Package initialization
├── main.py            # CLI entry point
├── builder.py         # Core build logic
├── config.py          # Configuration management
├── constants.py       # Constants and templates
├── spack_yaml.py      # Spack configuration
└── data/              # Data files
    └── patches/       # Source patches
```

### Adding New Slurm Versions

1. **Update constants.py**:
```python
SLURM_VERSIONS = {
    "25.11": {
        "url": "https://github.com/SchedMD/slurm/archive/refs/tags/slurm-25-11.tar.gz",
        "hash": "sha256:...",
        "spack_spec": "slurm@25.11"
    }
}
```

2. **Test the new version**:
```bash
uv run slurm-factory build 25.11
```

3. **Update documentation**:
- Add to supported versions table
- Update examples if needed

### Adding New Features

1. **Design**: Consider architecture and interfaces
2. **Implement**: Write clean, documented code
3. **Test**: Add comprehensive tests
4. **Document**: Update relevant documentation

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version**: Update version in pyproject.toml
2. **Update changelog**: Document changes in CHANGELOG.md
3. **Run tests**: Ensure all tests pass
4. **Tag release**: Create git tag
5. **Build packages**: Create distribution packages
6. **Publish**: Release to PyPI and GitHub

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code reviews and collaboration

## Getting Help

### For Contributors

- **Development questions**: GitHub Discussions
- **Code reviews**: Pull request comments
- **Design decisions**: GitHub Issues

### Resources

- **Architecture**: [Architecture Guide](/slurm-factory/architecture/)
- **API Reference**: [API Documentation](/slurm-factory/api-reference/)
- **Examples**: [Example Repository](https://github.com/vantagecompute/slurm-factory/tree/dev/examples)

