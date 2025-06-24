# Configuration

This guide covers configuring Pyestro for your environment.

## Configuration File Format

Pyestro uses JSON configuration files (YAML support planned). The main configuration file is `pyestro.json`.

### Basic Configuration

```json
{
    "maestro": {
        "project_dir": "/path/to/your/project",
        "work_dir": "./workdir",
        "dry_run": true,
        "force": false,
        "verbose": 1
    },
    "repositories": {
        "common_inv": "https://github.com/yourorg/inventory.git",
        "common_playbooks": "https://github.com/yourorg/playbooks.git"
    },
    "inventory": {
        "main": "./inventory"
    },
    "playbooks": {
        "common_playbooks": "./common_playbooks"
    },
    "ansible": {
        "managed": "Ansible managed. All local changes will be lost!",
        "timeout": 60,
        "scp_if_ssh": true,
        "galaxy_roles": ".ansible-galaxy-roles"
    }
}
```

## Configuration Sections

### Maestro Core Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `project_dir` | string | `$PWD` | Main project directory |
| `work_dir` | string | `"./workdir"` | Temporary working directory |
| `dry_run` | boolean | `true` | Default dry-run mode |
| `force` | boolean | `false` | Skip confirmation prompts |
| `verbose` | integer | `1` | Logging verbosity level |

### Repository Configuration

Define git repositories to clone and manage:

```json
{
    "repositories": {
        "maestro": "https://github.com/inofix/maestro",
        "common_inv": "https://github.com/inofix/common-inv",
        "common_playbooks": "https://github.com/zwischenloesung/common-playbooks",
        "packer_templates": "https://github.com/yourorg/packer.git",
        "vagrant_boxes": "https://github.com/yourorg/vagrant.git"
    }
}
```

### Inventory Configuration

Map inventory sources:

```json
{
    "inventory": {
        "main": "./inventory",
        "secondary": "./inventory2"
    }
}
```

### Playbook Configuration

Define playbook directories:

```json
{
    "playbooks": {
        "common_playbooks": "./common_playbooks",
        "custom_playbooks": "./playbooks"
    }
}
```

### Ansible Settings

Configure Ansible integration:

```json
{
    "ansible": {
        "managed": "Ansible managed. All local changes will be lost!",
        "timeout": 60,
        "scp_if_ssh": true,
        "galaxy_roles": ".ansible-galaxy-roles",
        "config_file": "./ansible.cfg"
    }
}
```

## Environment Variables

Override configuration with environment variables:

```bash
export PYESTRO_CONFIG="/path/to/custom/config.json"
export PYESTRO_DRY_RUN="false"
export PYESTRO_VERBOSE="2"
```

## Migration from Maestro

To migrate from the original bash Maestro:

```bash
# Analyze existing configuration
python pyestro.py migrate --analyze /path/to/.maestro

# Convert configuration
python pyestro.py migrate --convert /path/to/.maestro --output pyestro.json
```

### Example Migration

Original `.maestro` file:
```bash
maestrodir="/home/user/project"
workdir="./workdir"
toclone["common_inv"]="https://github.com/example/inv.git"
inventorydirs["main"]="./inventory"
```

Converted `pyestro.json`:
```json
{
    "maestro": {
        "project_dir": "/home/user/project",
        "work_dir": "./workdir"
    },
    "repositories": {
        "common_inv": "https://github.com/example/inv.git"
    },
    "inventory": {
        "main": "./inventory"
    }
}
```

## Validation

Validate your configuration:

```bash
# Check configuration syntax
python pyestro.py config validate

# Show current configuration
python pyestro.py config show
```

## Security Considerations

!!! warning "Sensitive Data"
    - Never commit authentication credentials to version control
    - Use environment variables for sensitive configuration
    - Consider using encrypted configuration for production

### Example Secure Configuration

```json
{
    "maestro": {
        "project_dir": "${PROJECT_DIR}",
        "work_dir": "./workdir"
    },
    "repositories": {
        "private_inv": "${PRIVATE_REPO_URL}"
    }
}
```

With environment variables:
```bash
export PROJECT_DIR="/secure/project/path"
export PRIVATE_REPO_URL="git@github.com:yourorg/private-inv.git"
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get up and running
- [Commands](../user-guide/commands.md) - Learn the CLI commands
- [CLI Reference](../reference/cli.md) - Complete command reference
