# Commands

This guide covers all the commands available in Pyestro.

## Command Structure

Pyestro uses a hierarchical command structure:

```bash
python pyestro.py [global-options] <command> [command-options] [arguments]
```

## Global Options

| Option | Description |
|--------|-------------|
| `--help, -h` | Show help message |
| `--version, -V` | Show version information |
| `--verbose, -v` | Increase verbosity |
| `--quiet, -q` | Suppress output |
| `--dry-run, -n` | Preview operations without executing |
| `--config, -c FILE` | Use alternative configuration file |

## Main Commands

### Project Creation

#### `create`
Create a new Pyestro project from a template.

```bash
python pyestro.py create <template> <project-name> [options]
python pyestro.py create --wizard
python pyestro.py create --list
```

**Template Creation:**
```bash
# Create basic project
python pyestro.py create basic my-project

# Create home automation project
python pyestro.py create home-network my-home

# Create with custom variables
python pyestro.py create basic my-project --var=work_dir=custom-workdir
```

**Interactive Mode:**
```bash
# Guided project creation
python pyestro.py create --wizard
```

**Available Templates:**
```bash
# List all templates
python pyestro.py create --list
```

Creates a complete project structure:
- `pyestro.json` configuration file
- `workdir/` directory
- `inventory/` reclass structure
- `playbooks/` Ansible directory
- `README.md` documentation
- `.gitignore` file

**Options:**
- `--var=key=value` - Set template variables
- `--dir=path` - Custom target directory

**Available Templates:**
- `basic` - Minimal Pyestro project
- `home-network` - Complete home automation setup

### Setup and Initialization

#### `init` (Legacy)
Initialize a new Pyestro project using the legacy method.

```bash
python pyestro.py init [--force]
```

!!! note "Deprecated"
    Use `pyestro create` instead for better project scaffolding.

Creates:
- `pyestro.json` configuration file
- `workdir/` directory
- `.gitignore` file

**Options:**
- `--force` - Overwrite existing files

#### `setup`
Setup project repositories and environment.

```bash
python pyestro.py setup [--dry-run]
```

**Actions:**
- Clones configured repositories
- Creates directory structure
- Validates configuration

### Configuration Management

#### `config show`
Display current configuration.

```bash
python pyestro.py config show [--format json|yaml]
```

#### `config validate`
Validate configuration file.

```bash
python pyestro.py config validate [--strict]
```

#### `config edit`
Edit configuration file.

```bash
python pyestro.py config edit [--editor EDITOR]
```

### Node Management

#### `nodes list`
List all available nodes.

```bash
python pyestro.py nodes list [--filter PATTERN] [--class CLASS] [--project PROJECT]
```

**Examples:**
```bash
# List all nodes
python pyestro.py nodes list

# Filter by pattern
python pyestro.py nodes list --filter "web*"

# Filter by class
python pyestro.py nodes list --class webserver

# Combine filters
python pyestro.py nodes list --filter "prod*" --class database
```

#### `nodes show`
Show detailed information about a specific node.

```bash
python pyestro.py nodes show NODENAME [--format json|yaml|table]
```

**Example:**
```bash
python pyestro.py nodes show web01.example.com
```

### Class Management

#### `classes list`
List all available classes.

```bash
python pyestro.py classes list [--filter PATTERN]
```

#### `classes show`
Show class details and which nodes use it.

```bash
python pyestro.py classes show CLASSNAME
```

### Ansible Operations

#### `ansible module`
Execute an Ansible module.

```bash
python pyestro.py ansible module MODULE [--args ARGS] [--hosts PATTERN] [--vars KEY=VALUE]
```

**Examples:**
```bash
# Ping all hosts
python pyestro.py ansible module ping

# Run command on specific hosts
python pyestro.py ansible module shell --args "uptime" --hosts "web*"

# Setup module with variables
python pyestro.py ansible module setup --hosts "db01" --vars gather_timeout=30
```

#### `ansible playbook`
Run an Ansible playbook.

```bash
python pyestro.py ansible playbook PLAYBOOK [--hosts PATTERN] [--vars KEY=VALUE] [--tags TAGS]
```

**Examples:**
```bash
# Run site playbook
python pyestro.py ansible playbook site.yml

# Run with specific hosts
python pyestro.py ansible playbook deploy.yml --hosts "production"

# Run specific tags
python pyestro.py ansible playbook site.yml --tags "nginx,ssl"
```

#### `ansible list-playbooks`
List available playbooks.

```bash
python pyestro.py ansible list-playbooks [--details]
```

#### `ansible ping`
Test connectivity to managed hosts.

```bash
python pyestro.py ansible ping [--hosts PATTERN]
```

#### `ansible galaxy-install`
Install Ansible Galaxy roles.

```bash
python pyestro.py ansible galaxy-install [--force] [--requirements FILE]
```

### Search Operations

#### `search`
Search for parameters across the inventory.

```bash
python pyestro.py search PARAMETER_PATH [--format json|table]
```

**Examples:**
```bash
# Search for a parameter
python pyestro.py search app:nginx:version

# Search with wildcard
python pyestro.py search "*:ssl:*"
```

### File Operations

#### `merge`
Merge files from storage to working directory.

```bash
python pyestro.py merge SOURCE DEST [--mode MODE] [--backup]
```

**Modes:**
- `file` - Merge individual files
- `dir` - Merge entire directories

#### `sync`
Synchronize files between directories.

```bash
python pyestro.py sync SOURCE DEST [--dry-run] [--delete]
```

### Status and Information

#### `status`
Show project status.

```bash
python pyestro.py status [--detailed]
```

**Information shown:**
- Configuration status
- Repository status
- Inventory status
- Connectivity status

#### `repos status`
Show repository status.

```bash
python pyestro.py repos status [--fetch]
```

#### `version`
Show version information.

```bash
python pyestro.py version [--detailed]
```

### Migration

#### `migrate`
Migrate from bash Maestro configuration.

```bash
python pyestro.py migrate --from PATH [--to FILE] [--analyze-only]
```

**Options:**
- `--from PATH` - Source .maestro file
- `--to FILE` - Output configuration file
- `--analyze-only` - Just analyze, don't convert

## Advanced Usage

### Combining Commands

Commands can be chained using shell operators:

```bash
# Update repos and run playbook
python pyestro.py repos update && python pyestro.py ansible playbook site.yml

# Check status before running
python pyestro.py status && python pyestro.py ansible ping
```

### Using Filters

Most commands support filtering:

```bash
# Complex node filtering
python pyestro.py nodes list --filter "prod-web*" --class "webserver" --project "ecommerce"

# Filter hosts for Ansible
python pyestro.py ansible module ping --hosts "staging-*"
```

### Environment Variables

Override behavior with environment variables:

```bash
# Force non-interactive mode
PYESTRO_FORCE=true python pyestro.py setup

# Set default dry-run
PYESTRO_DRY_RUN=true python pyestro.py ansible playbook site.yml
```

### Configuration Profiles

Use different configurations:

```bash
# Production configuration
python pyestro.py --config production.json status

# Development configuration  
python pyestro.py --config dev.json ansible ping
```

## Common Workflows

### Daily Operations
```bash
# Morning check
python pyestro.py status
python pyestro.py repos status
python pyestro.py ansible ping

# Deploy changes
python pyestro.py ansible playbook site.yml --dry-run
python pyestro.py ansible playbook site.yml
```

### Troubleshooting
```bash
# Verbose output for debugging
python pyestro.py --verbose 2 nodes show problematic-host

# Test connectivity
python pyestro.py ansible module ping --hosts problematic-host

# Check specific service
python pyestro.py ansible module service --args "name=nginx state=started" --hosts web-servers
```

### Development Workflow
```bash
# Setup development environment
python pyestro.py --config dev.json setup

# Test changes
python pyestro.py --config dev.json ansible playbook --tags testing dev.yml

# Validate inventory
python pyestro.py config validate
```

## Next Steps

- [Reclass Integration](reclass.md) - Working with reclass
- [Ansible Integration](ansible.md) - Advanced Ansible usage
- [CLI Reference](../reference/cli.md) - Complete command reference
