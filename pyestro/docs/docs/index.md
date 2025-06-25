# Pyestro Documentation

**Pyestro** is a modern Python-based configuration management orchestrator that provides a unified interface for managing heterogeneous infrastructure environments.

!!! info "What is Pyestro?"
    Pyestro acts as a bridge between metadata stored in reclass and various configuration management tools (primarily Ansible), enabling consistent management across multiple projects and environments.

## Key Features

- **🚀 Project Templates** - Quick-start templates for common scenarios (basic, home automation)
- **🐍 Modern Python Implementation** - Complete rewrite of the original bash-based Maestro
- **🔧 Configuration Management** - Unified interface for multiple CM tools
- **📊 Reclass Integration** - Leverage reclass as your knowledge base/CMDB
- **⚡ Ansible Support** - Execute modules, playbooks, and manage Galaxy roles
- **🔒 Security First** - Comprehensive input validation and sanitization
- **🌐 Multi-Environment** - Support for complex, heterogeneous infrastructures

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourname/pyestro.git
cd pyestro

# Install dependencies
pip install -r requirements.txt

# Create your first project
python pyestro.py create basic my-project
# OR use the interactive wizard
python pyestro.py create --wizard
```

### Basic Usage

```bash
# Show project status
python pyestro.py status

# List available nodes
python pyestro.py nodes list

# Execute Ansible ping on all nodes
python pyestro.py ansible module ping

# Run a playbook
python pyestro.py ansible playbook site.yml
```

## Architecture

Pyestro implements a three-layer architecture:

```
┌─────────────────┐    ┌─────────────────┐
│   Reclass       │    │   Plain Files   │
│  (metadata)     │    │ (config files)  │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
            ┌────────▼────────┐
            │    Pyestro      │
            │  (orchestrator) │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │     Ansible     │
            │  (config mgmt)  │
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │  Target Hosts   │
            └─────────────────┘
```

## Navigation

- **[Getting Started](getting-started/installation.md)** - Installation and initial setup
- **[User Guide](user-guide/commands.md)** - Daily usage and commands
- **[Developer Guide](developer-guide/architecture.md)** - Contributing and extending
- **[Reference](reference/cli.md)** - Complete command and configuration reference

## Community

- **Documentation**: You're reading it!
- **Issues**: [GitHub Issues](https://github.com/yourname/pyestro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourname/pyestro/discussions)

---

*Pyestro is the modern evolution of the original [Maestro](https://github.com/inofix/maestro) configuration management orchestrator.*
