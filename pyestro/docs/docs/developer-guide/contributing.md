# Contributing

Guidelines for contributing to the Pyestro project.

## Getting Started

Thank you for your interest in contributing to Pyestro! This guide will help you get started with development and contributions.

### Prerequisites

- **Python 3.8+** - Required for development
- **Git** - For version control
- **Virtual Environment** - Recommended for isolation

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourfork/pyestro.git
   cd pyestro
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Install in Development Mode**
   ```bash
   pip install -e .
   ```

5. **Verify Installation**
   ```bash
   python pyestro.py --version
   python -m pytest tests/
   ```

## Project Structure

```
pyestro/
├── pyestro/                  # Main package
│   ├── cli/                  # Command line interface
│   ├── core/                 # Core functionality
│   ├── parsers/              # Data parsers (reclass, etc.)
│   └── integrations/         # External tool integrations
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test fixtures
├── docs/                     # Documentation
├── examples/                 # Example configurations
├── pyproject.toml           # Project configuration
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md               # Project overview
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/new-feature-name
```

### 2. Make Changes

Follow the coding standards and guidelines below.

### 3. Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=pyestro

# Run specific test file
python -m pytest tests/unit/test_config.py
```

### 4. Update Documentation

Update relevant documentation in the `docs/` directory.

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

### 6. Push and Create PR

```bash
git push origin feature/new-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 100 characters (not 79)
- **String Quotes**: Use double quotes `"` for strings
- **Import Order**: Standard, third-party, local imports

### Code Formatting

Use the following tools for consistent formatting:

```bash
# Format code
black pyestro/ tests/

# Sort imports
isort pyestro/ tests/

# Lint code
flake8 pyestro/ tests/

# Type checking
mypy pyestro/
```

### Type Hints

Use type hints for all public APIs and complex functions:

```python
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

def process_nodes(
    nodes: List[str], 
    config: Dict[str, Any],
    dry_run: bool = True
) -> Optional[Dict[str, Any]]:
    """Process nodes with given configuration."""
    pass
```

### Documentation

All public functions and classes must have docstrings:

```python
def validate_configuration(config_path: Path) -> List[str]:
    """Validate configuration file and return list of errors.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        List of validation error messages
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        json.JSONDecodeError: If configuration file is invalid JSON
    """
    pass
```

## Testing Guidelines

### Test Structure

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from pyestro.core.config import MaestroConfig

class TestMaestroConfig:
    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config = MaestroConfig("test_config.json")
        data = config.load_config()
        assert isinstance(data, dict)
        assert "maestro" in data
    
    def test_load_invalid_config(self):
        """Test loading an invalid configuration file."""
        config = MaestroConfig("invalid_config.json")
        with pytest.raises(ConfigurationError):
            config.load_config()
    
    @patch('pyestro.core.config.Path.exists')
    def test_missing_config_file(self, mock_exists):
        """Test handling missing configuration file."""
        mock_exists.return_value = False
        config = MaestroConfig("missing.json")
        with pytest.raises(FileNotFoundError):
            config.load_config()
```

### Test Fixtures

Use fixtures for common test data:

```python
@pytest.fixture
def sample_config():
    """Provide sample configuration for testing."""
    return {
        "maestro": {
            "project_dir": "/tmp/test",
            "dry_run": True
        },
        "repositories": {
            "test_repo": "https://github.com/test/repo.git"
        }
    }

def test_config_validation(sample_config):
    """Test configuration validation with sample data."""
    config = MaestroConfig()
    config.data = sample_config
    errors = config.validate()
    assert len(errors) == 0
```

### Mocking External Dependencies

Mock external tools and services:

```python
@patch('subprocess.run')
def test_reclass_execution(mock_subprocess):
    """Test reclass command execution."""
    mock_subprocess.return_value.stdout = '{"nodes": {}}'
    mock_subprocess.return_value.returncode = 0
    
    from pyestro.parsers.reclass_parser import ReclassManager
    reclass = ReclassManager(Path("/test/inventory"))
    data = reclass.get_inventory_data()
    
    assert data == {"nodes": {}}
    mock_subprocess.assert_called_once()
```

## Documentation

### Documentation Structure

- **User Documentation**: Getting started, tutorials, how-to guides
- **API Reference**: Detailed API documentation
- **Developer Guide**: Architecture, contributing guidelines
- **Examples**: Working examples and use cases

### Writing Documentation

Use clear, concise language with practical examples:

```markdown
## Command Usage

The `nodes list` command displays all available nodes:

```bash
python pyestro.py nodes list --filter "web*"
```

This command will:
1. Query the reclass inventory
2. Filter nodes matching the pattern
3. Display results in table format
```

### Building Documentation

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material

# Serve documentation locally
cd docs/
mkdocs serve

# Build static documentation
mkdocs build
```

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass (`python -m pytest`)
- [ ] Code is formatted (`black`, `isort`)
- [ ] Type checking passes (`mypy`)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Code Review**: Maintainers review code quality and design
3. **Testing**: Changes are tested in development environment
4. **Merge**: PR is merged after approval

## Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9.5]
- Pyestro version: [e.g., 1.0.0]

## Additional Context
Any other relevant information.
```

### Feature Requests

Use the feature request template:

```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered.

## Additional Context
Any other relevant information.
```

## Security

### Reporting Security Issues

Do not report security vulnerabilities through public GitHub issues. Instead:

1. Email security issues to: security@pyestro.org
2. Include "SECURITY" in the subject line
3. Provide detailed description and steps to reproduce

### Security Best Practices

- **Input Validation**: Always validate and sanitize user inputs
- **Path Traversal**: Prevent directory traversal attacks
- **Command Injection**: Sanitize shell commands
- **Secrets**: Never commit secrets or credentials
- **Dependencies**: Keep dependencies updated

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Documentation**: Primary reference material

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Help

### Documentation
- [User Guide](../user-guide/commands.md)
- [API Reference](api.md)
- [Architecture Guide](architecture.md)

### Community Support
- GitHub Issues for bugs and feature requests
- GitHub Discussions for questions and help

### Development Questions
- Review existing code and tests for examples
- Check the architecture documentation
- Ask questions in GitHub Discussions

Thank you for contributing to Pyestro! 🎉
