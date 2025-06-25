# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Maestro** configuration management orchestrator project, which consists of two major components:

1. **Maestro (Legacy)** - Original bash-based orchestrator (`maestro.sh`)
2. **Pyestro** - Modern Python rewrite located in `pyestro/` directory

The project provides a unified interface for managing heterogeneous infrastructure environments using reclass as a knowledge base and various configuration management tools (primarily Ansible).

## Architecture

### Dual Implementation Structure
- **Root Level**: Original bash Maestro implementation with documentation
- **pyestro/** - Complete Python rewrite with modern architecture
- **Shared Concepts**: Both implementations use reclass for metadata and Ansible for configuration management

### Core Components
- **Reclass Integration**: Hierarchical node classification system
- **Ansible Integration**: Playbook and module execution
- **Git Repository Management**: Multi-repository synchronization
- **File Operations**: Config file merging and synchronization

## Development Commands

### Pyestro (Python Version)
```bash
# Navigate to Python implementation
cd pyestro/

# Development setup
pip install -e ".[dev]"
pre-commit install

# Run application
python pyestro.py --help

# Testing and validation
python pyestro.py --validate
pytest  # when tests are implemented
ruff check .
black --check .
mypy pyestro/
```

### Original Maestro (Bash Version)
```bash
# Run from project root
./maestro.sh help
./maestro.sh init
./maestro.sh status
```

### Documentation
```bash
# Serve documentation locally
cd pyestro/docs/
pip install mkdocs mkdocs-material
mkdocs serve
# Open http://localhost:8000
```

## Code Organization

### Pyestro Python Structure
- **pyestro/cli/main.py** - Command-line interface
- **pyestro/core/** - Core functionality (config, git, file ops, validation)
- **pyestro/parsers/** - Data parsers (reclass integration)
- **pyestro/integrations/** - CM tool integrations (Ansible)

### Configuration
- **pyestro.json** - Python version configuration (JSON schema validated)
- **.maestro** - Bash version configuration file
- **pyproject.toml** - Python package configuration with dev dependencies

## Key Development Practices

### Python Code Standards
- Type hints required throughout
- Input validation via `pyestro/core/validation.py`
- No shell injection - use direct Python calls
- Comprehensive error handling and logging
- Modular design with single responsibility principle

### Security Considerations
- All user inputs must be validated and sanitized
- No eval() or shell command execution
- Path validation for file operations
- Secure git operations with verification

### Testing Requirements
- Unit tests for all new functionality (when test framework is implemented)
- Configuration validation before execution
- Dry-run support for all operations
- Integration tests with actual tools (ansible, git, reclass)

## Dependencies

### System Requirements
- Python 3.9+ (for Pyestro)
- Git
- Bash and standard Unix utilities (for legacy Maestro)
- rsync

### Python Dependencies (pyestro/)
- **Core**: click, pydantic, pyyaml, gitpython, paramiko, jinja2, rich, structlog
- **Dev**: pytest, pytest-cov, black, mypy, pre-commit, ruff

### Optional Tools
- ansible, ansible-playbook (for CM integration)
- reclass (for metadata management)
- ssh (for host connectivity)

## Common Workflows

### Adding New Features to Pyestro
1. Create feature branch
2. Implement in appropriate module (core/, parsers/, integrations/)
3. Add type hints and validation
4. Update CLI if needed
5. Test with dry-run mode
6. Update documentation

### Migration Support
- Both implementations can coexist
- Migration tools available in Pyestro CLI
- Configuration converters between formats

## Important Files

### Configuration Examples
- `pyestro/pyestro.example.json` - Example Pyestro configuration
- Documentation in `pyestro/docs/docs/getting-started/configuration.md`

### Key Documentation
- `README.md` - Project overview and migration info
- `MAESTRO-SPEC.md` - Detailed original Maestro specification
- `WIKI-ARCHITECTURE.md` - Architectural concepts and design
- `pyestro/README.md` - Pyestro-specific documentation
- `pyestro/DEVELOPMENT.md` - Development progress and status

## Migration Context

This project is in active migration from bash to Python. When working on this codebase:
- Prefer Pyestro (Python) for new features
- Maintain compatibility concepts between versions
- Focus on security improvements in Python version
- Document migration paths for users

The Python rewrite addresses security, maintainability, and extensibility issues while preserving the core architectural concepts that make Maestro effective.