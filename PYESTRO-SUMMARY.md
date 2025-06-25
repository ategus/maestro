# Pyestro Summary

**Pyestro** is the modern Python successor to Maestro, designed for orchestrating configuration management environments with enhanced security, maintainability, and functionality.

## 🚀 Quick Start

```bash
# Navigate to Pyestro directory
cd pyestro/

# Install dependencies
pip install -e .

# Create configuration
cp pyestro.example.json pyestro.json
# Edit pyestro.json with your settings

# Initialize project
python pyestro.py --init

# Sync repositories
python pyestro.py --sync

# Generate reclass data
python pyestro.py --reclass

# Run Ansible
python pyestro.py --ansible
```

## 📁 Project Structure

```
pyestro/
├── pyestro/              # Core Python modules
│   ├── cli/              # Command-line interface
│   ├── core/             # Core functionality (config, git, file ops)
│   ├── integrations/     # Ansible integration
│   └── parsers/          # Reclass parser
├── docs/                 # MkDocs documentation
├── pyestro.py           # Main CLI script
├── pyestro.json         # Configuration file
└── pyproject.toml       # Python project metadata
```

## ⚙️ Key Configuration

Edit `pyestro.json` to configure:

- **repos**: Git repositories to manage
- **reclass**: Reclass configuration and paths
- **ansible**: Ansible playbook settings
- **paths**: Working directories and file locations

Example minimal configuration:
```json
{
  "repos": {
    "my-config": {
      "url": "git@github.com:user/config.git",
      "branch": "main"
    }
  },
  "reclass": {
    "nodes_path": "nodes",
    "classes_path": "classes"
  },
  "ansible": {
    "playbook": "site.yml"
  }
}
```

## 🎯 Common Commands

| Command | Description |
|---------|-------------|
| `python pyestro.py --init` | Initialize project structure |
| `python pyestro.py --sync` | Sync all repositories |
| `python pyestro.py --reclass` | Generate reclass inventory |
| `python pyestro.py --ansible` | Run Ansible playbooks |
| `python pyestro.py --validate` | Validate configuration |
| `python pyestro.py --status` | Show project status |

## 📖 Documentation

- **[Full Documentation](./pyestro/docs/)** - Comprehensive guides and reference
- **[Getting Started](./pyestro/docs/docs/getting-started/)** - Installation and setup
- **[Home Network Tutorial](./pyestro/docs/docs/tutorials/home-network-setup.md)** - Real-world example
- **[Migration Guide](./pyestro/docs/docs/reference/migration.md)** - Migrating from Maestro

### Browse Documentation Locally

```bash
cd pyestro/docs/
pip install mkdocs mkdocs-material
mkdocs serve
# Open http://localhost:8000
```

## 🔧 Key Features

### Modern Python Architecture
- Type hints and comprehensive error handling
- Modular design with clear separation of concerns
- Extensive logging and validation

### Enhanced Security
- Input validation and sanitization
- Secure Git operations with SSH key support
- Configuration schema validation

### Flexible Configuration
- JSON configuration with schema validation
- Support for multiple inventory backends (reclass, Ansible, Jsonnet, Consul)
- Environment-specific overrides

### Improved Integration
- Native Ansible integration with inventory generation
- Git workflow automation
- File operation utilities with backup support

## 🏠 Example: Home Network Setup

Pyestro includes a complete tutorial for setting up a home network with:
- Raspberry Pi running Home Assistant
- NAS server with media services
- Network monitoring and automation

See [Home Network Tutorial](./pyestro/docs/docs/tutorials/home-network-setup.md) for the complete guide.

## 🔄 Migration from Maestro

If you're migrating from the original Bash-based Maestro:

1. **Configuration**: Convert `.maestro` config to `pyestro.json` format
2. **Structure**: Reclass and Ansible structures remain compatible
3. **Commands**: Similar workflow with enhanced CLI options
4. **Validation**: Additional safety checks and validation

See the [Migration Guide](./pyestro/docs/docs/reference/migration.md) for detailed steps.

## 🛠️ Development

For contributing to Pyestro:

```bash
# Development setup
cd pyestro/
pip install -e .[dev]

# Run tests (when implemented)
pytest

# Build documentation
cd docs/
mkdocs build
```

## 📋 Requirements

- Python 3.8+
- Git
- Ansible (for Ansible integration)
- SSH access to repositories

## 📞 Support

- **Documentation**: [./pyestro/docs/](./pyestro/docs/)
- **Examples**: [Tutorial configurations](./pyestro/docs/docs/tutorials/)
- **Legacy**: [Maestro documentation](./README.md) for original version

---

**Ready to get started?** Check out the [Quick Start Guide](./pyestro/docs/docs/getting-started/quickstart.md) or try the [Home Network Tutorial](./pyestro/docs/docs/tutorials/home-network-setup.md)!
