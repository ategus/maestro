# Maestro (Original) Project Specification

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

#### File Operations
```bash
# Rsync configuration
rsync_options="-a -m --exclude=.keep"

# Merge settings
merge_only_this_subdir=""
merge_mode="dir"

# Files to ignore on unmerge
unmerge_ignore=(
    "_packages.wiki"
)
```

#### System Tools
```bash
# Required system tools with paths
declare -A sys_tools
sys_tools=(
    ["_ansible"]="/usr/bin/ansible"
    ["_ansible_playbook"]="/usr/bin/ansible-playbook"
    ["_ansible_galaxy"]="/usr/bin/ansible-galaxy"
    ["_awk"]="/usr/bin/gawk"
    ["_git"]="/usr/bin/git"
    ["_reclass"]="/usr/bin/reclass"
    ["_rsync"]="/usr/bin/rsync"
    # ... additional tools
)

# Tools that require special handling in dry-run/root mode
danger_tools=(
    "_ansible"
    "_ansible_playbook"
    "_ansible_galaxy"
    "_rsync"
    # ... additional dangerous tools
)
```

## Reclass Integration

### Parser Implementation
- **AWK-based**: Complex AWK scripts for parsing reclass JSON output
- **Project Extraction**: Automatic project namespace detection
- **Parameter Processing**: Deep parameter tree navigation
- **Variable Substitution**: Template variable replacement

### Inventory Processing
```bash
# Get node data
reclass -b "$inventorydir" -n "$nodename" --output json

# Get complete inventory
reclass -b "$inventorydir" --inventory --output json
```

### Class Organization
```
classes/
├── admin/           # Administrative classes
├── location/        # Geographic/datacenter classes
├── project/         # Project-specific classes
├── role/           # Functional roles
├── service/        # Service definitions
└── app/            # Application classes
```

## File Processing

### Merge Operation
- **Source**: Storage directories
- **Target**: `workdir/`
- **Method**: rsync with configurable options
- **Modes**: File-level or directory-level merging

### Unmerge Operation
- **Source**: `workdir/`
- **Target**: Storage directories
- **Safety**: Backup creation
- **Filtering**: Ignore specified file patterns

### Rsync Configuration
```bash
# Default options
rsync_options="-a -m --exclude=.keep"

# Archive mode: permissions, timestamps, symlinks
# Prune empty directories
# Exclude .keep files
```

## Security Considerations

### Input Sanitization
```awk
# Basic input sanitization in AWK
/<|>|\$|\|`/ {
    next
}
```

### Tool Safety
- **Dry-run Mode**: Dangerous tools disabled in dry-run
- **Root Operations**: Sudo handling for privileged operations
- **Path Validation**: Basic path traversal protection

### Command Injection
- **Limited Validation**: Basic shell metacharacter filtering
- **Tool Wrapping**: Controlled execution of external tools

## Performance Characteristics

### Scalability
- **Node Limit**: Tested with moderate inventories (<500 nodes)
- **Memory Usage**: AWK-based processing, relatively memory efficient
- **Processing Speed**: Sequential operations, no parallelization

### Caching
- **Inventory Cache**: Reclass output cached in `.inventory/`
- **Repository Cache**: Local git repositories
- **No Session Cache**: Fresh reclass queries each run

## Error Handling

### Error Categories
1. **Tool Missing**: Required system tools not found
2. **Configuration Error**: Invalid config file or missing settings
3. **Reclass Error**: Inventory parsing failures
4. **Ansible Error**: Playbook or module execution failures
5. **File System Error**: Permission or access issues

### Error Response
- **Exit Codes**: Standard Unix exit codes
- **Error Messages**: Basic error reporting to stderr
- **Logging**: Limited logging to stdout/stderr
- **Recovery**: Manual intervention required

## Testing and Validation

### Validation Levels
- **Config Validation**: Basic config file existence checks
- **Tool Validation**: System tool availability verification
- **Inventory Validation**: Reclass syntax and structure checks
- **Connectivity Testing**: SSH connectivity to managed hosts

### Testing Modes
- **Dry-run Mode**: Preview operations without execution
- **Parser Test**: Show parsed data without actions
- **Interactive Mode**: Confirmation prompts for destructive operations

## Dependencies

### System Requirements
- **Operating System**: Linux/Unix (bash, standard utilities)
- **Shell**: Bash 4.0+
- **AWK**: GNU AWK (gawk)
- **Git**: Version control operations
- **Rsync**: File synchronization

### Optional Dependencies
- **Reclass**: Metadata management
- **Ansible**: Configuration management
- **SSH**: Host connectivity
- **Sudo**: Privileged operations

## Migration Considerations

### From Maestro to Pyestro
1. **Configuration Migration**: `.maestro` → `pyestro.json`
2. **Command Mapping**: Bash commands → Python CLI
3. **Feature Gaps**: Identify missing functionality
4. **Data Compatibility**: Ensure reclass inventory compatibility

### Compatibility Matrix
| Feature | Maestro (Bash) | Pyestro (Python) | Migration Notes |
|---------|----------------|------------------|-----------------|
| Configuration | .maestro file | JSON/YAML | Format conversion needed |
| Reclass | AWK parsing | Python parsing | Output format compatible |
| Ansible | Direct calls | Python wrapper | Command mapping required |
| File Ops | rsync/bash | Python/rsync | Logic preservation needed |
| Search | grep/AWK | Python | Enhanced capabilities possible |

## Known Limitations

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

## Future Evolution

### Pyestro Advantages
- **Maintainability**: Python more maintainable than complex bash/AWK
- **Error Handling**: Better error handling and recovery
- **Testing**: Unit testing capabilities
- **Security**: Enhanced input validation and sanitization
- **Performance**: Potential for optimization and parallelization
- **Features**: Enhanced search, filtering, and reporting capabilities

### Migration Path
1. **Phase 1**: Feature parity implementation
2. **Phase 2**: Enhanced capabilities
3. **Phase 3**: Deprecation of bash version
4. **Phase 4**: Pure Python ecosystem

## Conclusion

The original Maestro represents a practical solution to multi-environment configuration management challenges. While functional, its bash/AWK implementation presents maintenance and scalability challenges that the Python-based Pyestro project aims to address while preserving the core architectural concepts and workflows that make Maestro effective.
