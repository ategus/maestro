# Quick Start

This guide will get you up and running with Pyestro in just a few minutes.

## 1. Create Your Project

### Option A: Interactive Project Creation (Recommended)

```bash
# Interactive wizard for guided setup
python pyestro.py create --wizard
```

### Option B: Direct Project Creation

```bash
# Create a basic project
python pyestro.py create basic my-project

# Create a home automation project
python pyestro.py create home-network my-home
```

### Option C: See Available Templates

```bash
# List all available project templates
python pyestro.py create --list
```

This creates a complete project structure with:
- `pyestro.json` - Main configuration file
- `workdir/` - Working directory for operations
- `inventory/` - Reclass inventory structure
- `playbooks/` - Ansible playbooks directory
- `README.md` - Project documentation
- `.gitignore` - Git ignore patterns

## 2. Navigate to Your Project

```bash
# Change to your new project directory
cd my-project  # or whatever you named your project
```

## 3. Review and Customize Configuration

The generated `pyestro.json` is already configured with sensible defaults. Review and customize as needed:

```json
{
  "maestro_dir": ".",
  "work_dir": "./workdir",
  "dry_run": false,
  "verbose": 1,
  "repositories": {},
  "inventory_dirs": {
    "local": "./inventory"
  },
  "playbook_dirs": {
    "local": "./playbooks"
  },
  "ansible": {
    "config_file": "./ansible.cfg",
    "managed_banner": "Ansible managed: my-project.",
    "timeout": 60
  }
}
```

## 4. Setup Project Environment

```bash
# Validate your configuration
python pyestro.py config validate

# Setup repositories and dependencies
python pyestro.py setup
```

This will:
- Validate your configuration
- Clone any configured repositories
- Set up the working directory structure
- Install required dependencies
- Set up inventory structure
- Validate configuration

## 4. Verify Your Setup

```bash
# Check project status
python pyestro.py status

# List available nodes (if inventory is configured)
python pyestro.py nodes list

# Show configuration
python pyestro.py config show
```

## 5. Basic Operations

### Working with Nodes

```bash
# List all nodes
python pyestro.py nodes list

# Show details for a specific node
python pyestro.py nodes show hostname.example.com

# Filter nodes by class
python pyestro.py nodes list --class webserver
```

### Ansible Operations

```bash
# Test connectivity to all nodes
python pyestro.py ansible module ping

# Execute a command on specific nodes
python pyestro.py ansible module shell -a "uptime" --hosts web*

# Run a playbook
python pyestro.py ansible playbook site.yml --dry-run
```

## Common Workflows

### 1. Daily Operations
```bash
# Check project status
python pyestro.py status

# Update repositories
python pyestro.py repos update

# Test connectivity
python pyestro.py ansible ping
```

### 2. Configuration Changes
```bash
# Validate changes (dry run)
python pyestro.py ansible playbook site.yml --dry-run

# Apply changes
python pyestro.py ansible playbook site.yml
```

### 3. Troubleshooting
```bash
# Verbose output
python pyestro.py --verbose 2 status

# Check specific node
python pyestro.py nodes show problematic-host.example.com

# Test specific host connectivity
python pyestro.py ansible module ping --hosts problematic-host.example.com
```

## Next Steps

- [Configuration Guide](configuration.md) - Detailed configuration options
- [Command Reference](../reference/cli.md) - Complete command documentation
- [User Guide](../user-guide/commands.md) - Advanced usage patterns
