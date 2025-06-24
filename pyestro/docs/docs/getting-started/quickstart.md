# Quick Start

This guide will get you up and running with Pyestro in just a few minutes.

## 1. Initialize Your Project

```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize Pyestro configuration
python pyestro.py init
```

This creates:
- `pyestro.json` - Main configuration file
- `workdir/` - Temporary working directory
- `.gitignore` - Git ignore patterns

## 2. Configure Your Project

Edit the generated `pyestro.json`:

```json
{
    "maestro": {
        "project_dir": "/path/to/your/project",
        "work_dir": "./workdir",
        "dry_run": true,
        "verbose": 1
    },
    "repositories": {
        "common_inv": "https://github.com/yourorg/inventory.git",
        "common_playbooks": "https://github.com/yourorg/playbooks.git"
    },
    "inventory": {
        "main": "./inventory"
    }
}
```

## 3. Setup Repositories

```bash
# Download and setup required repositories
python pyestro.py setup
```

This will:
- Clone configured repositories
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
