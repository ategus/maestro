# Original Maestro Specification

This document provides a comprehensive specification of the original bash-based Maestro configuration management orchestrator, which serves as the foundation for the modern Python-based Pyestro implementation.

## Overview

Maestro is a bash-based configuration management orchestrator that provides a unified interface for managing heterogeneous infrastructure environments. Originally developed to bridge the gap between metadata stored in reclass and various configuration management tools, primarily Ansible.

## Project Background

### Historical Context
- **Origin**: Started with cfengine automation
- **Evolution**: Moved through various CM tools (cfengine, ansible, salt, debops)
- **Challenge**: Different customers using different CM systems
- **Solution**: Unified orchestrator using reclass as common knowledge base

### Philosophy
> "The central idea behind maestro is to build a knowledge base (CMDB) that can be used by several configuration management tools. It must be flexible enough to be split up as needed and simple enough such that one can work on several projects without having to think too much."

## Architecture

### Three-Layer Design
```
BACKEND0 (meta-data):              BACKEND1 (concrete-data):
    ,---------.                         ,---------.
   |`----------'--.                    |`----------'--.
   |  reclass0 |---'--.                |  confix0  |---'--.
   |           |s1 |---'               |           |1  |---'<--.
    `---------'    |.. |                `---------'    |.. |   |
        `---------'    |                    `---------'    |   |
            \---------'                     /   `---------'    |
              \| _______________________  |/                   |
               ,'                       `.                     |
CONNECTOR:    (       m a e s t r o       )                    |
               `._______________________,'\                    |
                  /     /      |   _        \                  |
                 V     V   _   V  |C| ____    \                |
             __________   | | ___ |F||Temp|     \              |
            (=========='  |d||   ||E||late|       \            |
CONFIGURATION    |\ Ansible |  |e|| S ||n||    |        |(plain     |
MANAGEMENT:      || \       |  |b|| a ||g|| j2 | _____  | files)   /
                ||  |~~~~~ |  |o|| l ||i|| .. || ... | |        /
                ||  |~~~~~ |  |p|| t ||n||    || ... | |      /
                ||  |~~~~~ |  |s||   ||e||    || ... | |    /
                (|  |______| .|_||___||_||____||_____| |  /
                 \  |                                /  /
                   \| |      |      |  |   |       /  /
                      |      |      |  |   |     /  /
                      V      V      V  V   V    V /
    MACHINES:     [ host0 ][ host1 ] ... [ hostN ]
```

## Core Components

### 1. Configuration System
- **Format**: Bash configuration file (`.maestro`)
- **Hierarchy**: System → Global → User → Local → Command-line
- **Location Precedence**:
  1. `/etc/maestro`
  2. `/usr/etc/maestro`
  3. `/usr/local/etc/maestro`
  4. `~/.maestro`
  5. `./maestro` or `./.maestro`
  6. Command-line specified config

### 2. Repository Management
- **Git Integration**: Clone and manage multiple repositories
- **Repository Types**:
  - `maestro` - The orchestrator itself
  - `common_inv` - Common inventory/metadata
  - `common_playbooks` - Shared Ansible playbooks
  - `packer_templates` - Infrastructure templates
  - `vagrant_boxes` - Development environments

### 3. Reclass Integration
- **Knowledge Base**: Primary metadata backend
- **Inventory Management**: Merged inventory in `.inventory/`
- **Node Processing**: AWK-based parsing of reclass output
- **Class Organization**: Hierarchical class structure

### 4. Ansible Integration
- **Module Execution**: Direct ansible module calls
- **Playbook Management**: Discover and execute playbooks
- **Galaxy Support**: Role management
- **Configuration**: Dynamic ansible.cfg generation

## Command Interface

### Primary Commands

#### Initialization and Setup
```bash
# Initialize environment with all defined repos
maestro.sh init

# Update reclass environment without pulling repos
maestro.sh reinit
```

#### Node and Class Management
```bash
# List hosts sorted by applications
maestro.sh applications-list [app]
maestro.sh als [app]

# List hosts sorted by class
maestro.sh classes-list [class]
maestro.sh cls [class]

# List all nodes
maestro.sh nodes-list
maestro.sh nls

# Show node details
maestro.sh node-show nodename
maestro.sh ns nodename
```

#### Ansible Operations
```bash
# Execute ansible module
maestro.sh ansible-module module [args] [vars] [options]
maestro.sh ansible module [args] [vars] [options]

# Run playbook
maestro.sh ansible-play playbook [vars] [options]
maestro.sh play playbook [vars] [options]

# Loop playbook with items
maestro.sh ansible-play-loop playbook itemkey=val1:val2 [vars] [options]
maestro.sh ploop playbook itemkey=val1:val2 [vars] [options]

# List available playbooks
maestro.sh ansible-plays-list [play]
maestro.sh pls [play]
```

#### File Operations
```bash
# Merge files from storage to workdir
maestro.sh merge [subdir] [rsync-options]
maestro.sh mg [subdir] [rsync-options]

# Unmerge files from workdir back to storage
maestro.sh unmerge [subdir] [rsync-options]
maestro.sh umg [subdir] [rsync-options]
```

#### Search Operations
```bash
# Search for parameter across inventory
maestro.sh search pattern

# Search for class references
maestro.sh search-class classpattern

# Search in playbooks
maestro.sh search-in-playbooks pattern

# Search external variables
maestro.sh search-external pattern

# Search reclass variables
maestro.sh search-reclass pattern
```

#### Status and Information
```bash
# Test host connectivity and show system info
maestro.sh status
maestro.sh ss

# Show help
maestro.sh help
```

### Command-Line Options

#### Filtering Options
```bash
# Filter by class
-C, --class CLASS

# Filter by host/node
-H, --host HOST
-N, --node NODE

# Filter by project
-P, --project PROJECT
```

#### Execution Options
```bash
# Dry run mode
-n, --dry-run

# Force execution without prompts
-f, --force

# Interactive mode (ask before changes)
-i, --interactive

# Parser test mode
-p, --parser-test

# Verbose output
-v, --verbose [level]

# Quiet mode
-q, --quiet

# Custom work directory
-w, --workdir DIRECTORY
```

#### Configuration Options
```bash
# Alternative config file
-c, --config CONFFILE

# Show version
-V, --version

# Show help
-h, --help
```

## Configuration Schema

### Core Configuration Variables

#### Project Settings
```bash
# Maestro's project directory
maestrodir="$PWD"

# Repository directory name
maestro_repo_dir_name="maestro"
maestro_repo_dir="$maestrodir/$maestro_repo_dir_name"

# Working directory
workdir="./workdir"

# Execution modes
force=1          # 0=force, 1=interactive
dryrun=1         # 0=dry-run, 1=execute
needsroot=1      # Whether root privileges needed
verbose="1"      # Verbosity level
```

#### Repository Configuration
```bash
# Repositories to clone
declare -A toclone
toclone=(
    ["maestro"]="https://github.com/inofix/maestro"
    ["common_inv"]="https://github.com/inofix/common-inv"
    ["common_playbooks"]="https://github.com/zwischenloesung/common-playbooks"
)
```

#### Directory Mappings
```bash
# Reclass inventory sources
declare -A inventorydirs
inventorydirs=(
    ["main"]="./inventory"
)

# Ansible playbook directories
declare -A playbookdirs
playbookdirs=(
    ["common_playbooks"]="./common_playbooks"
)

# Additional local directories
declare -A localdirs
localdirs=(
    ["packer_templates"]="./packer_templates"
    ["vagrant_boxes"]="./vagrant_boxes"
)
```

#### Ansible Configuration
```bash
# Ansible defaults
ansible_managed="Ansible managed. All local changes will be lost!"
ansible_timeout="60"
ansible_scp_if_ssh="True"
ansible_galaxy_roles=".ansible-galaxy-roles"
ansible_config_default="$maestrodir/ansible.cfg"

# Galaxy roles file
galaxyroles="galaxy/roles.yml"

# Connection script
ansible_connect="$maestro_repo_dir/reclass-ansible.sh"

# Additional options
ansibleoptions=""
```

## Migration from Maestro to Pyestro

### Key Differences

| Aspect | Original Maestro | Pyestro |
|--------|------------------|---------|
| **Language** | Bash + AWK | Python 3.8+ |
| **Configuration** | `.maestro` file | JSON/YAML |
| **Parsing** | AWK scripts | Python libraries |
| **Error Handling** | Basic | Comprehensive |
| **Testing** | Manual | Unit tests |
| **Security** | Basic | Enhanced validation |
| **Performance** | Sequential | Potential parallelization |

### Migration Path

1. **Configuration Conversion**
   ```bash
   # Original
   maestrodir="/path/to/project"
   toclone["common_inv"]="https://github.com/example/inv.git"
   
   # Pyestro equivalent
   {
     "maestro": {"project_dir": "/path/to/project"},
     "repositories": {"common_inv": "https://github.com/example/inv.git"}
   }
   ```

2. **Command Mapping**
   ```bash
   # Original Maestro
   maestro.sh nodes-list --class webserver
   maestro.sh ansible-module ping
   maestro.sh ansible-play site.yml
   
   # Pyestro equivalent
   python pyestro.py nodes list --class webserver
   python pyestro.py ansible module ping
   python pyestro.py ansible playbook site.yml
   ```

3. **Feature Enhancement**
   - Enhanced search capabilities
   - Better error messages
   - Structured logging
   - Input validation
   - Dry-run improvements

### Compatibility Considerations

!!! warning "Breaking Changes"
    - Configuration file format changed from bash to JSON/YAML
    - Command syntax slightly different
    - Some advanced AWK parsing may need adjustment
    - Error output format changed

!!! success "Preserved Features"
    - Core workflow unchanged
    - Reclass integration compatible
    - Ansible integration compatible
    - Repository management logic preserved

## Technical Implementation Details

### AWK Parser (Original)
The original Maestro used complex AWK scripts for parsing reclass JSON output:

```awk
# Example AWK parser snippet
BEGIN {
    split(target_var, target_vars, ":")
    spaces="  "
    i=1
    target="^"spaces""target_vars[i]":"
    deeper="^"spaces"[ -] "
}
/^parameters:$/ {
    mode="param"
    next
}
# ... complex parsing logic
```

### Python Implementation (Pyestro)
Pyestro replaces AWK with Python JSON parsing:

```python
import json
import subprocess

def get_node_data(node_name):
    result = subprocess.run([
        "reclass", "-b", inventory_dir, 
        "-n", node_name, "--output", "json"
    ], capture_output=True, text=True)
    return json.loads(result.stdout)
```

## Known Limitations of Original Maestro

### Technical Limitations
- **AWK Complexity**: Complex parsing logic difficult to maintain
- **Error Handling**: Limited error recovery capabilities  
- **Parallelization**: No concurrent operations support
- **Memory Usage**: Large inventories may cause issues
- **Platform Support**: Unix/Linux only

### Functional Limitations
- **Search Capabilities**: Basic pattern matching only
- **Validation**: Limited input validation
- **Logging**: No structured logging
- **Configuration**: Limited configuration validation
- **Security**: Basic input sanitization

## Conclusion

The original Maestro represents a practical solution to multi-environment configuration management challenges. While functional, its bash/AWK implementation presents maintenance and scalability challenges that the Python-based Pyestro project aims to address while preserving the core architectural concepts and workflows that make Maestro effective.

### Key Takeaways

1. **Proven Architecture**: The three-layer architecture works well in practice
2. **Reclass Integration**: Using reclass as a knowledge base is effective
3. **Unified Interface**: Single tool for multiple CM systems reduces complexity
4. **Evolution Need**: Modern implementation needed for maintainability and features

### Next Steps

- Review [Pyestro Specification](../developer-guide/architecture.md) for the modern implementation
- See [Migration Guide](migration.md) for transitioning from Maestro to Pyestro
- Check [Command Reference](cli.md) for Pyestro command syntax
