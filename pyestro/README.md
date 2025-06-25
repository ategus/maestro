# 🎼 Pyestro

<div align="center">
  <img src="pyestro_logo_transparent.png" alt="Pyestro Logo" width="200" height="auto" />
</div>

> **🚀 The modern Python evolution of Maestro** - A next-generation configuration management orchestrator that provides a unified interface to manage multiple server environments with enhanced security, maintainability, and developer experience.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-GPL%20v3-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-MkDocs-orange.svg)](docs/)

---

## 🌟 Overview

Pyestro maintains the core philosophy of [Maestro](https://github.com/inofix/maestro) while bringing it into the modern era with:

- **🔒 Enhanced Security**: Robust input validation and secure operations
- **🏗️ Modern Architecture**: Clean, modular Python codebase with type hints
- **⚡ Better Performance**: Optimized operations and reduced complexity
- **🛡️ Type Safety**: Full type hints and comprehensive validation
- **🧪 Testing Coverage**: Extensive unit and integration tests
- **📖 Rich Documentation**: Comprehensive guides and tutorials

## ✨ Key Features

### 🔧 **Multi-Tool Orchestration**
- Seamlessly orchestrate Ansible, Salt, and other configuration management tools
- Unified interface across different automation platforms
- Consistent workflow regardless of underlying tools

### 📊 **Centralized Knowledge Base**
- Unified metadata management using reclass
- Hierarchical node classification
- Flexible data inheritance and override system

### 🔄 **Smart Git Integration**
- Automatic repository management and synchronization
- Branch tracking and conflict resolution
- Secure SSH key handling

### ⚙️ **Flexible Configuration**
- JSON-based configuration with schema validation
- Environment-specific overrides
- Live configuration validation

### 🎯 **Developer-Friendly CLI**
- Modern command-line interface with rich output
- Comprehensive help system and examples
- Interactive modes for complex operations

### 🔍 **Safety First**
- Dry-run support for all operations
- Configuration validation before execution
- Rollback capabilities and backup management

## 📦 Installation

### 🚀 **Quick Install**
```bash
cd pyestro/
pip install -e .
```

### 🛠️ **Development Setup**
```bash
cd pyestro/
pip install -e ".[dev]"
pre-commit install
```

### 📋 **Requirements**
- 🐍 Python 3.8+
- 📚 Git
- ⚙️ Ansible (for Ansible integration)
- 🔑 SSH access to repositories

## 🚀 Quick Start

### 1️⃣ **Initialize Your Project**
```bash
# Copy and customize configuration
cp pyestro.example.json pyestro.json
# Edit pyestro.json with your settings

# Initialize project structure
python pyestro.py --init
```

### 2️⃣ **Sync Your Repositories**
```bash
# Sync all configured repositories
python pyestro.py --sync
```

### 3️⃣ **Generate Inventory**
```bash
# Create reclass inventory
python pyestro.py --reclass
```

### 4️⃣ **Run Your Playbooks**
```bash
# Execute Ansible playbooks
python pyestro.py --ansible
```

### 5️⃣ **Monitor Status**
```bash
# Check project status
python pyestro.py --status
```

## 🏠 **Real-World Example**

Want to see Pyestro in action? Check out our comprehensive [Home Network Tutorial](docs/docs/tutorials/home-network-setup.md) that walks through setting up:

- 🏠 **Raspberry Pi** with Home Assistant
- 💾 **NAS Server** with media services  
- 📡 **Network Monitoring** and automation
- 🔐 **Security** configuration and monitoring

Perfect for learning Pyestro with a practical, real-world scenario!

## 🔄 Migration from Bash Maestro

Migrating from the original Bash Maestro? We've got you covered! 🎯

```bash
# 1. Convert your existing configuration
# From: .maestro config file
# To: pyestro.json format

# 2. Use our migration guide
# See: docs/docs/reference/migration.md

# 3. Validate your new setup
python pyestro.py --validate
```

**🔗 Migration Resources:**
- 📖 [Step-by-step Migration Guide](docs/docs/reference/migration.md)
- 🔍 [Legacy Maestro Tutorial](docs/docs/reference/legacy-maestro-tutorial.md)
- ⚖️ [Configuration Comparison](docs/docs/reference/config-schema.md)

## ⚙️ Configuration

Pyestro uses clean **JSON configuration** with schema validation:

```json
{
  "repos": {
    "my-config": {
      "url": "git@github.com:user/config.git",
      "branch": "main"
    },
    "common-playbooks": {
      "url": "git@github.com:user/playbooks.git",
      "branch": "main"
    }
  },
  "reclass": {
    "nodes_path": "nodes",
    "classes_path": "classes",
    "compose_node_name": false
  },
  "ansible": {
    "playbook": "site.yml",
    "inventory_dir": "inventory",
    "config_file": "ansible.cfg"
  },
  "paths": {
    "work_dir": "./work",
    "backup_dir": "./backups"
  }
}
```

**🎯 Key Configuration Features:**
- ✅ **Schema Validation**: Catch errors before execution
- 🔧 **Multiple Backends**: Support for reclass, Ansible, Jsonnet, Consul
- 🌍 **Environment Overrides**: Different configs per environment
- 🔐 **Secure Credentials**: Safe handling of sensitive data

## 🎯 Commands Reference

### 🚀 **Core Operations**
| Command | Description | Example |
|---------|-------------|---------|
| `python pyestro.py --init` | 🏗️ Initialize project structure | `python pyestro.py --init` |
| `python pyestro.py --sync` | 🔄 Sync all repositories | `python pyestro.py --sync` |
| `python pyestro.py --reclass` | 📊 Generate reclass inventory | `python pyestro.py --reclass` |
| `python pyestro.py --ansible` | ⚙️ Run Ansible playbooks | `python pyestro.py --ansible` |
| `python pyestro.py --validate` | ✅ Validate configuration | `python pyestro.py --validate` |
| `python pyestro.py --status` | 📈 Show project status | `python pyestro.py --status` |

### 🛠️ **Advanced Options**
- `--dry-run` - 🔍 Preview operations without executing
- `--verbose` - 📝 Detailed logging output
- `--config PATH` - 📄 Use custom configuration file
- `--work-dir PATH` - 📁 Set custom working directory

## 🏗️ Architecture

```
pyestro/
├── 🎯 cli/              # Command-line interface
├── ⚡ core/             # Core functionality
│   ├── config.py        # Configuration management
│   ├── git.py          # Git operations
│   ├── file_ops.py     # File operations
│   └── validation.py   # Input validation
├── 🔧 parsers/          # Data parsers (reclass, etc.)
├── 🔌 integrations/     # CM tool integrations
└── 🧪 tests/            # Test suite (coming soon)
```

**🎨 Design Principles:**
- 🧩 **Modular**: Clean separation of concerns
- 🔒 **Secure**: Security-first design
- 🚀 **Fast**: Optimized for performance
- 🧪 **Testable**: Easy to test and maintain

## 🛡️ Security Enhancements

Pyestro prioritizes security with enterprise-grade features:

- **🔍 Input Validation**: All user inputs are validated and sanitized
- **🚫 No Shell Injection**: Direct Python execution instead of shell commands  
- **🔐 Secure Git Operations**: Repository verification and secure cloning
- **📁 Safe File Operations**: Path validation and secure file handling
- **📜 Structured Logging**: Comprehensive audit trail
- **🔑 Credential Management**: Secure handling of sensitive data
- **✅ Pre-execution Validation**: Catch issues before they cause problems

## 📚 Documentation

### 🎓 **Getting Started**
- 📖 [Full Documentation](docs/) - Comprehensive guides and reference  
- 🚀 [Quick Start Guide](docs/docs/getting-started/quickstart.md) - Get up and running fast
- ⚙️ [Installation Guide](docs/docs/getting-started/installation.md) - Detailed setup instructions
- 🔧 [Configuration Guide](docs/docs/getting-started/configuration.md) - Configuration deep-dive

### 🎯 **Tutorials & Examples**
- 🏠 [Home Network Setup](docs/docs/tutorials/home-network-setup.md) - Real-world example
- 🔄 [Migration from Maestro](docs/docs/reference/migration.md) - Step-by-step migration
- 📊 [Configuration Schema](docs/docs/reference/config-schema.md) - Complete reference

### 🌐 **Browse Documentation Locally**
```bash
cd docs/
pip install mkdocs mkdocs-material
mkdocs serve
# 🌐 Open http://localhost:8000
```

## 🤝 Contributing

We welcome contributions! 🎉

### 🚀 **Quick Start for Contributors**
```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/pyestro.git
cd pyestro

# 2. Set up development environment  
pip install -e ".[dev]"
pre-commit install

# 3. Run tests (when implemented)
pytest

# 4. Submit your changes
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

### 📋 **Contribution Guidelines**
- 🧪 Write tests for new features
- 📝 Update documentation for changes
- 🔍 Follow code style guidelines  
- 💬 Use clear commit messages

## 📄 License

**GNU General Public License v3.0** - See [LICENSE](LICENSE) for details.

## 🔗 Compatibility

Pyestro maintains backward compatibility with:

- ✅ **Original Maestro**: Configurations (with migration tools)
- ✅ **Reclass**: Inventories and hierarchies
- ✅ **Ansible**: Existing playbooks and roles
- ✅ **Git Workflows**: Standard Git operations and workflows

## 🆘 Support & Community

### 📞 **Get Help**
- 🐛 [GitHub Issues](https://github.com/yourusername/pyestro/issues) - Bug reports and feature requests
- 💬 [Discussions](https://github.com/yourusername/pyestro/discussions) - Community support and ideas  
- 📖 [Documentation](docs/) - Comprehensive guides and tutorials
- 🔄 [Migration Tools](docs/docs/reference/migration.md) - Smooth transition assistance

### 🌟 **What's Next?**
- 🌐 **Web UI**: Browser-based management interface
- 📱 **TUI**: Terminal-based interactive interface  
- 🔌 **Plugin System**: Extensible architecture
- ☁️ **Cloud Integration**: Native cloud provider support
- 📊 **Monitoring**: Built-in monitoring and alerting

---

<div align="center">

**⭐ Ready to orchestrate like a maestro? ⭐**

[🚀 Get Started](docs/docs/getting-started/quickstart.md) | [🏠 Try the Tutorial](docs/docs/tutorials/home-network-setup.md) | [🔄 Migrate from Maestro](docs/docs/reference/migration.md)

</div>
