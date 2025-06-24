# Pyestro

A modern Python rewrite of [Maestro](https://github.com/inofix/maestro) - a configuration management orchestrator that provides a unified interface to manage multiple server environments using different configuration management systems.

## Overview

Pyestro maintains the core philosophy of Maestro while providing:
- **Enhanced Security**: Proper input validation and sanitization
- **Modern Architecture**: Clean, modular Python codebase
- **Better Error Handling**: Comprehensive exception handling and logging
- **Type Safety**: Full type hints and validation
- **Comprehensive Testing**: Unit and integration test coverage

## Features

- **Multi-CM Support**: Orchestrate Ansible, Salt, and other configuration management tools
- **Unified Metadata**: Centralized knowledge base using reclass
- **Git Integration**: Automatic repository management and synchronization
- **Flexible Configuration**: YAML-based configuration with validation
- **Rich CLI**: Modern command-line interface with helpful output
- **Dry-run Support**: Safe preview mode for all operations

## Installation

### From Source
```bash
cd pyestro
pip install -e .
```

### Development Installation
```bash
cd pyestro
pip install -e ".[dev]"
pre-commit install
```

## Quick Start

1. **Initialize a new project**:
   ```bash
   pyestro init
   ```

2. **Configure your environments**:
   ```bash
   # Edit pyestro.yaml with your inventory and playbook directories
   pyestro config show
   ```

3. **List available nodes**:
   ```bash
   pyestro nodes list
   ```

4. **Execute Ansible playbooks**:
   ```bash
   pyestro ansible playbook site.yml
   ```

5. **Check host status**:
   ```bash
   pyestro status
   ```

## Migration from Bash Maestro

Pyestro provides compatibility tools to migrate from the original bash implementation:

```bash
# Convert existing .maestro config
pyestro migrate --from-bash .maestro

# Verify configuration
pyestro config validate
```

## Configuration

Pyestro uses YAML configuration files instead of bash associative arrays:

```yaml
# pyestro.yaml
maestro_dir: "."
work_dir: "./workdir"
dry_run: true
verbose: 1

repositories:
  maestro: "https://github.com/inofix/maestro"
  common_inv: "https://github.com/inofix/common-inv"
  example_inv: "https://github.com/inofix/example-inv"
  common_playbooks: "https://github.com/inofix/common-playbooks"

inventory_dirs:
  common_inv: "./common_inv"
  example_inv: "./example_inv"

playbook_dirs:
  common_playbooks: "./common_playbooks"

local_dirs:
  any_confix: "none"
  packer_templates: "none"
  vagrant_boxes: "none"

ansible:
  config: "./ansible.cfg"
  managed: "Ansible managed. All local changes will be lost!"
  timeout: 60
  galaxy_roles: ".ansible-galaxy-roles"
```

## Commands

### Core Operations
- `pyestro init` - Initialize new project
- `pyestro config` - Configuration management
- `pyestro nodes` - Node operations
- `pyestro ansible` - Ansible integration
- `pyestro merge` - File synchronization
- `pyestro status` - Host connectivity checks

### Development
- `pyestro migrate` - Migration utilities
- `pyestro search` - Search inventory and playbooks
- `pyestro validate` - Validate configurations

## Architecture

```
pyestro/
├── cli/           # Command-line interface
├── core/          # Core functionality
├── parsers/       # Data parsers (reclass, etc.)
├── integrations/  # CM tool integrations
├── utils/         # Utility functions
└── tests/         # Test suite
```

## Security Improvements

- **Input Validation**: All user inputs are validated and sanitized
- **No Shell Injection**: Direct Python execution instead of shell commands
- **Secure Git Operations**: Repository verification and secure cloning
- **Safe File Operations**: Path validation and secure file handling
- **Structured Logging**: Comprehensive audit trail

## Contributing

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -e ".[dev]"`
4. Run tests: `pytest`
5. Submit a pull request

## License

GNU General Public License v3.0 - See [LICENSE](LICENSE) for details.

## Compatibility

Pyestro maintains compatibility with:
- Original Maestro configurations (with migration tools)
- Reclass inventories
- Existing Ansible playbooks
- Standard Git workflows

## Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: See `docs/` directory for detailed guides
- **Migration**: Use built-in migration tools for smooth transition
