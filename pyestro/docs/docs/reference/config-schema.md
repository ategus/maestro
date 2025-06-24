# Configuration Schema

Complete reference for Pyestro configuration options.

## Configuration File Format

Pyestro uses JSON configuration files with optional YAML support. The configuration follows a hierarchical structure with well-defined sections.

## Schema Overview

```json
{
    "maestro": { ... },
    "repositories": { ... },
    "inventory": { ... },
    "playbooks": { ... },
    "ansible": { ... },
    "rsync": { ... }
}
```

## Schema Specification

### Root Schema

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `maestro` | object | Yes | Core Pyestro settings |
| `repositories` | object | No | Git repository definitions |
| `inventory` | object | No | Reclass inventory configuration |
| `playbooks` | object | No | Ansible playbook directories |
| `ansible` | object | No | Ansible-specific settings |
| `rsync` | object | No | File synchronization options |

### Maestro Section

Core Pyestro configuration options.

```json
{
    "maestro": {
        "project_dir": "/path/to/project",
        "work_dir": "./workdir",
        "dry_run": true,
        "force": false,
        "verbose": 1
    }
}
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `project_dir` | string | `$PWD` | Main project directory |
| `work_dir` | string | `"./workdir"` | Temporary working directory |
| `dry_run` | boolean | `true` | Default dry-run mode |
| `force` | boolean | `false` | Skip confirmation prompts |
| `verbose` | integer | `1` | Logging verbosity (0-3) |

### Repositories Section

Git repository configuration for cloning and management.

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

| Property | Type | Description |
|----------|------|-------------|
| `<repo_name>` | string | Git repository URL (HTTPS or SSH) |

**Supported URL formats:**
- HTTPS: `https://github.com/user/repo.git`
- SSH: `git@github.com:user/repo.git`
- Local: `/path/to/local/repo`

### Inventory Section

Inventory configuration supporting multiple backends.

```json
{
    "inventory": {
        "backend": "reclass",
        "sources": {
            "main": "./inventory",
            "secondary": "./inventory2",
            "common": "/shared/inventory"
        }
    }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `backend` | string | Inventory backend: `reclass`, `ansible`, `jsonnet`, `consul` |
| `sources` | object | Backend-specific source configuration |

#### Supported Backends

**Reclass (default):**
```json
{
    "inventory": {
        "backend": "reclass",
        "sources": {
            "main": "./inventory"
        }
    }
}
```

**Ansible Native:**
```json
{
    "inventory": {
        "backend": "ansible",
        "sources": {
            "inventory_file": "./hosts.yml",
            "group_vars": "./group_vars",
            "host_vars": "./host_vars"
        }
    }
}
```

**Jsonnet:**
```json
{
    "inventory": {
        "backend": "jsonnet",
        "sources": {
            "main": "./inventory.jsonnet",
            "lib_paths": ["./lib", "./vendor"]
        }
    }
}
```

**Consul:**
```json
{
    "inventory": {
        "backend": "consul",
        "sources": {
            "endpoint": "https://consul.company.com:8500",
            "prefix": "ansible/inventory",
            "token": "${CONSUL_TOKEN}"
        }
    }
}
```

**Directory Structure Expected:**
```
inventory/
├── classes/
│   ├── admin/
│   ├── location/
│   ├── project/
│   ├── role/
│   ├── service/
│   └── app/
└── nodes/
    ├── project1/
    └── project2/
```

### Playbooks Section

Ansible playbook directory configuration.

```json
{
    "playbooks": {
        "common_playbooks": "./common_playbooks",
        "custom_playbooks": "./playbooks",
        "roles": "./roles"
    }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `<playbook_dir_name>` | string | Path to playbook directory |

### Ansible Section

Ansible-specific configuration options.

```json
{
    "ansible": {
        "managed": "Ansible managed. All local changes will be lost!",
        "timeout": 60,
        "scp_if_ssh": true,
        "galaxy_roles": ".ansible-galaxy-roles",
        "config_file": "./ansible.cfg",
        "vault_password_file": "./vault_pass",
        "private_key_file": "~/.ssh/id_rsa"
    }
}
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `managed` | string | `"Ansible managed..."` | Ansible managed file header |
| `timeout` | integer | `60` | SSH connection timeout (seconds) |
| `scp_if_ssh` | boolean | `true` | Use SCP for file transfer |
| `galaxy_roles` | string | `".ansible-galaxy-roles"` | Galaxy roles directory |
| `config_file` | string | `"./ansible.cfg"` | Ansible configuration file path |
| `vault_password_file` | string | `null` | Vault password file path |
| `private_key_file` | string | `null` | SSH private key file path |

### Rsync Section

File synchronization options using rsync.

```json
{
    "rsync": {
        "options": "-a -m --exclude=.keep",
        "exclude_patterns": [".git", "*.pyc", "__pycache__"],
        "dry_run_option": "--dry-run",
        "verbose_option": "-v"
    }
}
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `options` | string | `"-a -m --exclude=.keep"` | Default rsync options |
| `exclude_patterns` | array | `[]` | Additional exclude patterns |
| `dry_run_option` | string | `"--dry-run"` | Dry-run flag for rsync |
| `verbose_option` | string | `"-v"` | Verbose flag for rsync |

## Complete Example

```json
{
    "maestro": {
        "project_dir": "/home/user/infrastructure",
        "work_dir": "./workdir",
        "dry_run": true,
        "force": false,
        "verbose": 2
    },
    "repositories": {
        "maestro": "https://github.com/inofix/maestro",
        "common_inv": "git@github.com:company/common-inventory.git",
        "common_playbooks": "https://github.com/company/ansible-playbooks.git",
        "custom_roles": "/local/path/to/roles"
    },
    "inventory": {
        "backend": "reclass",
        "sources": {
            "main": "./inventory",
            "testing": "./test-inventory"
        }
    },
    "playbooks": {
        "common_playbooks": "./common_playbooks",
        "site_playbooks": "./site-playbooks"
    },
    "ansible": {
        "managed": "This file is managed by Pyestro - do not edit manually!",
        "timeout": 120,
        "scp_if_ssh": true,
        "galaxy_roles": ".ansible-galaxy-roles",
        "config_file": "./ansible.cfg",
        "vault_password_file": "./vault_pass.txt"
    },
    "rsync": {
        "options": "-a -m --exclude=.keep --exclude=*.tmp",
        "exclude_patterns": [
            ".git",
            "*.pyc",
            "__pycache__",
            "*.log"
        ]
    }
}

## User-Friendly Features

### Auto-Detection and Smart Defaults

Pyestro can automatically detect common configurations:

```bash
# Auto-detect project structure and generate config
python pyestro.py init --auto-detect

# Interactive configuration wizard
python pyestro.py init --interactive

# Generate config from existing .maestro file
python pyestro.py init --from-maestro .maestro
```

### Configuration Templates

Pre-built templates for common scenarios:

```bash
# List available templates
python pyestro.py templates list

# Initialize from template
python pyestro.py init --template ansible-reclass
python pyestro.py init --template kubernetes-ops
python pyestro.py init --template simple-automation
```

### Validation and Health Checks

```bash
# Comprehensive configuration validation
python pyestro.py doctor

# Check repository connectivity
python pyestro.py config check-repos

# Validate inventory structure
python pyestro.py config check-inventory

# Test ansible connectivity
python pyestro.py config check-ansible
```
```

## Environment Variable Overrides

Configuration values can be overridden using environment variables:

| Environment Variable | Configuration Path | Type |
|---------------------|-------------------|------|
| `PYESTRO_CONFIG` | N/A | Configuration file path |
| `PYESTRO_PROJECT_DIR` | `maestro.project_dir` | string |
| `PYESTRO_WORK_DIR` | `maestro.work_dir` | string |
| `PYESTRO_DRY_RUN` | `maestro.dry_run` | boolean |
| `PYESTRO_FORCE` | `maestro.force` | boolean |
| `PYESTRO_VERBOSE` | `maestro.verbose` | integer |

**Example:**
```bash
export PYESTRO_DRY_RUN=false
export PYESTRO_VERBOSE=3
python pyestro.py status
```

## Configuration Validation

### JSON Schema Validation

Pyestro validates configuration against a JSON schema. Common validation errors:

#### Invalid Type
```json
{
    "maestro": {
        "verbose": "high"  // Should be integer
    }
}
```
**Error:** `verbose must be an integer between 0 and 3`

#### Missing Required Property
```json
{
    "repositories": {
        "common_inv": "https://github.com/example/inv.git"
    }
    // Missing maestro section
}
```
**Error:** `maestro section is required`

#### Invalid Path
```json
{
    "maestro": {
        "project_dir": "../../../etc/passwd"  // Path traversal attempt
    }
}
```
**Error:** `project_dir contains invalid path components`

### Validation Commands

```bash
# Validate current configuration
python pyestro.py config validate

# Validate specific file
python pyestro.py config validate --file custom.json

# Strict validation (additional checks)
python pyestro.py config validate --strict
```

## Configuration Migration

### From Bash Maestro

Original `.maestro` format:
```bash
maestrodir="/home/user/project"
workdir="./workdir"
toclone["common_inv"]="https://github.com/example/inv.git"
inventorydirs["main"]="./inventory"
ansible_timeout="60"
```

Equivalent `pyestro.json`:
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
    },
    "ansible": {
        "timeout": 60
    }
}
```

### Migration Command

```bash
python pyestro.py migrate --from .maestro --to pyestro.json
```

## YAML Support (Planned)

Future versions will support YAML configuration:

```yaml
maestro:
  project_dir: /home/user/infrastructure
  work_dir: ./workdir
  dry_run: true
  verbose: 2

repositories:
  common_inv: git@github.com:company/inventory.git
  playbooks: https://github.com/company/playbooks.git

inventory:
  main: ./inventory
  testing: ./test-inventory

ansible:
  timeout: 120
  galaxy_roles: .ansible-galaxy-roles
```

## Security Considerations

### Sensitive Data

!!! warning "Sensitive Information"
    Never commit sensitive data to version control:
    - SSH private keys
    - Vault passwords
    - API tokens
    - Database credentials

### Best Practices

1. **Use Environment Variables** for sensitive data
2. **File Permissions** - Restrict config file access (600)
3. **Path Validation** - All paths are validated for security
4. **URL Validation** - Repository URLs are validated

### Example Secure Configuration

```json
{
    "maestro": {
        "project_dir": "${PROJECT_DIR}"
    },
    "repositories": {
        "private_inv": "${PRIVATE_REPO_URL}"
    },
    "ansible": {
        "vault_password_file": "${VAULT_PASSWORD_FILE}",
        "private_key_file": "${SSH_KEY_FILE}"
    }
}
```

With environment file (`.env`):
```bash
PROJECT_DIR=/secure/project/path
PRIVATE_REPO_URL=git@github.com:company/private-inv.git
VAULT_PASSWORD_FILE=/secure/vault_pass
SSH_KEY_FILE=/secure/ssh_key
```

## Troubleshooting

### Common Configuration Issues

#### Issue: Configuration file not found
**Solution:** Ensure file exists and use absolute path

#### Issue: Invalid JSON syntax
**Solution:** Validate JSON syntax using online validator

#### Issue: Permission denied
**Solution:** Check file permissions and ownership

#### Issue: Repository clone fails
**Solution:** Verify repository URL and SSH key access

For more help, see:
- [Getting Started](../getting-started/configuration.md)
- [Migration Guide](migration.md)
- [CLI Reference](cli.md)
