# Maestro/Pyestro Project Specification

## Overview

Maestro/Pyestro is a configuration management orchestrator that provides a unified interface for managing heterogeneous infrastructure environments. It acts as a bridge between metadata stored in reclass and various configuration management tools (primarily Ansible), enabling consistent management across multiple projects and environments.

## Project Vision

"The central idea behind maestro is to build a knowledge base (CMDB) that can be used by several configuration management tools. It must be flexible enough to be split up as needed and simple enough such that one can work on several projects without having to think too much."

## Core Concepts

### Architecture Pattern: 'Stable' Approach
- **'Pet' vs. 'herd'** - Maestro implements the 'stable' approach
- Provides consistency across diverse customer environments
- Supports multiple configuration management systems simultaneously
- Enables sharing and comparison of projects/hosts

### Three-Layer Architecture

```
BACKEND0 (meta-data)    ←→    BACKEND1 (concrete-data)
    [reclass]                      [plain files]
        ↓                               ↓
    CONNECTOR: [maestro/pyestro]
        ↓
CONFIGURATION MANAGEMENT: [Ansible, Salt, etc.]
        ↓
    MACHINES: [host0, host1, ..., hostN]
```

## Functional Requirements

### 1. Configuration Management
- **Primary Format**: JSON configuration with YAML support
- **Migration Support**: Ability to migrate from bash .maestro config files
- **Validation**: Comprehensive input validation and sanitization
- **Security**: Protection against injection attacks and malicious input

### 2. Repository Management
- **Git Integration**: Clone, pull, and manage multiple git repositories
- **Repository Types**:
  - `maestro` - The orchestrator itself
  - `common_inv` - Common inventory/metadata
  - `example_inv` - Example inventory structure
  - `common_playbooks` - Shared Ansible playbooks
  - `packer_templates` - Infrastructure templates
  - `vagrant_boxes` - Development environments
- **Batch Operations**: Manage multiple repositories simultaneously

### 3. Reclass Integration
- **Knowledge Base**: Use reclass as the primary metadata backend
- **Node Management**: List, filter, and query nodes
- **Class Management**: Organize and query reclass classes
- **Parameter Search**: Deep search through parameter hierarchies
- **Inventory Validation**: Verify reclass inventory integrity
- **Filtering**: Support for node, class, and project filters with wildcards

### 4. Ansible Integration
- **Module Execution**: Execute arbitrary Ansible modules
- **Playbook Management**: Discover and execute playbooks
- **Galaxy Integration**: Manage Ansible Galaxy roles
- **Host Patterns**: Dynamic host pattern generation from filters
- **Configuration**: Generate ansible.cfg files
- **Connection Testing**: Verify connectivity to managed hosts

### 5. File Operations
- **Synchronization**: Rsync-based file synchronization with Python fallback
- **Merging**: Directory and file merging capabilities
- **Backup**: Safe file operations with backup support
- **Templates**: Support for Jinja2 templates and plain files

### 6. Command Line Interface
- **Subcommands**: Organized command structure
- **Interactive Mode**: Confirmation prompts for destructive operations
- **Dry Run**: Preview mode for all operations
- **Verbose Output**: Configurable logging levels
- **Help System**: Comprehensive help and usage information

## Technical Requirements

### 1. Programming Language
- **Primary**: Python 3.8+
- **Dependencies**: Minimal external dependencies
- **Packaging**: Standard Python packaging (pyproject.toml)

### 2. Core Dependencies
- **Required**:
  - `subprocess` - External command execution
  - `pathlib` - Path manipulation
  - `json` - Configuration parsing
  - `argparse` - CLI argument parsing
  - `logging` - Structured logging
- **Optional**:
  - `yaml` - YAML configuration support
  - `jinja2` - Template processing
  - `git` - Git operations (fallback to command line)

### 3. Security Requirements
- **Input Validation**: All user inputs must be validated and sanitized
- **Path Traversal Protection**: Prevent directory traversal attacks
- **Command Injection Protection**: Sanitize all shell commands
- **Privilege Escalation**: Support for sudo operations where necessary
- **Secrets Management**: Avoid logging sensitive information

### 4. Performance Requirements
- **Scalability**: Handle inventories with 1000+ nodes
- **Caching**: Cache reclass data to avoid repeated queries
- **Parallel Operations**: Support concurrent operations where safe
- **Memory Efficiency**: Stream large outputs rather than loading in memory

## Command Specification

### Setup and Initialization
```bash
# Initialize new project environment
pyestro init

# Setup project with repository cloning
pyestro setup [--dry-run]

# Migrate from bash maestro configuration
pyestro migrate --from /path/to/.maestro
```

### Configuration Management
```bash
# Show current configuration
pyestro config show

# Validate configuration
pyestro config validate

# Edit configuration
pyestro config edit
```

### Inventory Operations
```bash
# List all nodes
pyestro nodes list [--filter PATTERN] [--class CLASS] [--project PROJECT]

# Show node details
pyestro nodes show NODENAME

# List classes
pyestro classes list

# Show class details  
pyestro classes show CLASSNAME

# Search parameters
pyestro search PARAMETER_PATH
```

### Ansible Operations
```bash
# Execute Ansible module
pyestro ansible module MODULE [ARGS] [--hosts PATTERN]

# Run playbook
pyestro ansible playbook PLAYBOOK [--hosts PATTERN] [--vars KEY=VALUE]

# List available playbooks
pyestro ansible list-playbooks

# Test connectivity
pyestro ansible ping [--hosts PATTERN]

# Install Galaxy roles
pyestro ansible galaxy-install
```

### File Operations
```bash
# Merge files/directories
pyestro merge SOURCE DEST [--mode MODE]

# Unmerge (restore backup)
pyestro unmerge SOURCE

# Sync files
pyestro sync SOURCE DEST [--dry-run]
```

### Status and Information
```bash
# Show project status
pyestro status

# Check repository status
pyestro repos status

# Show version information
pyestro version

# Show help
pyestro help [COMMAND]
```

## Configuration Schema

### Primary Configuration File: `pyestro.json`

```json
{
    "maestro": {
        "project_dir": "/path/to/project",
        "work_dir": "./workdir",
        "dry_run": true,
        "force": false,
        "verbose": 1
    },
    "repositories": {
        "maestro": "https://github.com/inofix/maestro",
        "common_inv": "https://github.com/inofix/common-inv",
        "common_playbooks": "https://github.com/zwischenloesung/common-playbooks"
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
        "galaxy_roles": ".ansible-galaxy-roles",
        "config_file": "./ansible.cfg"
    },
    "rsync": {
        "options": "-a -m --exclude=.keep"
    }
}
```

## Class Organization (Reclass Structure)

### Recommended Class Hierarchy
```
classes/
├── admin/           # Administrative classes
├── location/        # Geographic/datacenter classes
├── project/         # Project-specific classes
├── role/           # Functional roles
├── service/        # Service definitions
└── app/            # Application classes
    ├── apache/
    ├── nginx/
    ├── java/
    │   ├── init.yml
    │   └── jre/
    │       ├── init.yml
    │       └── 8.yml
    └── ...

nodes/
├── project1/
│   ├── web01.example.com.yml
│   └── db01.example.com.yml
└── project2/
    └── ...
```

### Parameter Namespacing
- **Dictionary Format**: `app[apache][config_files]`
- **Flat Format**: `app__apache__config_files`
- **Search Support**: Deep parameter path searching

## File Structure

### Project Layout
```
pyestro/
├── pyproject.toml           # Project configuration
├── README.md               # User documentation
├── DEVELOPMENT.md          # Development notes
├── pyestro.py             # CLI entry point
├── pyestro.example.json   # Example configuration
└── pyestro/               # Main package
    ├── __init__.py
    ├── cli/               # Command line interface
    │   ├── __init__.py
    │   └── main.py
    ├── core/              # Core functionality
    │   ├── __init__.py
    │   ├── config.py      # Configuration management
    │   ├── git.py         # Git operations
    │   ├── file_ops.py    # File operations
    │   └── validation.py  # Input validation
    ├── parsers/           # Data parsers
    │   ├── __init__.py
    │   └── reclass_parser.py
    └── integrations/      # External tool integrations
        ├── __init__.py
        └── ansible.py
```

### Generated Files and Directories
```
project_root/
├── .gitignore             # Version control exclusions
├── pyestro.json          # Runtime configuration
├── workdir/              # Temporary working directory
├── .inventory/           # Merged reclass inventory
├── ansible.cfg           # Generated Ansible configuration
├── .ansible-galaxy-roles/ # Downloaded Galaxy roles
├── inventory/            # Primary reclass inventory
├── common_playbooks/     # Shared playbooks
├── common_inv/           # Common inventory
└── logs/                 # Application logs
```

## Error Handling

### Error Categories
1. **Configuration Errors**: Invalid configuration files or missing settings
2. **Validation Errors**: Invalid user input or parameters
3. **External Tool Errors**: Reclass, Ansible, or Git command failures
4. **File System Errors**: Permission issues, missing files, disk space
5. **Network Errors**: Repository access, connectivity issues

### Error Response Strategy
- **Graceful Degradation**: Continue operations where possible
- **Clear Messages**: Provide actionable error messages
- **Exit Codes**: Standard Unix exit codes for script integration
- **Logging**: Comprehensive logging for debugging

## Testing Requirements

### Unit Tests
- **Coverage Target**: >80% code coverage
- **Test Categories**: Configuration, validation, file operations, CLI
- **Mock Objects**: External dependencies (git, ansible, reclass)

### Integration Tests
- **End-to-End**: Full workflow testing
- **Configuration**: Test with various configuration scenarios
- **External Tools**: Test with actual reclass/ansible installations

### Performance Tests
- **Large Inventories**: Test with 1000+ nodes
- **Concurrent Operations**: Multi-threaded safety
- **Memory Usage**: Memory leak detection

## Compatibility Requirements

### Operating Systems
- **Primary**: Linux distributions (Ubuntu, CentOS, RHEL)
- **Secondary**: macOS
- **Limited**: Windows (via WSL)

### Python Versions
- **Minimum**: Python 3.8
- **Recommended**: Python 3.9+
- **Testing**: Latest stable Python version

### External Tools
- **Required**: git
- **Optional**: reclass, ansible, rsync
- **Version Detection**: Automatic tool version detection

## Migration Path

### From Bash Maestro
1. **Configuration Migration**: Convert .maestro to pyestro.json
2. **Command Mapping**: Provide bash-to-python command equivalents
3. **Feature Parity**: Ensure all bash features are available
4. **Transition Period**: Support both versions during migration

### Migration Commands
```bash
# Analyze existing maestro configuration
pyestro migrate --analyze /path/to/.maestro

# Convert configuration
pyestro migrate --convert /path/to/.maestro

# Validate migration
pyestro migrate --validate
```

## Development Milestones

### Phase 1: Core Foundation ✅
- Configuration management
- Basic CLI structure
- Input validation
- File operations

### Phase 2: Integration ✅
- Reclass integration
- Ansible integration
- Git operations
- Repository management

### Phase 3: Advanced Features
- YAML configuration support
- Template processing
- Plugin system
- Web interface

### Phase 4: Production Ready
- Comprehensive testing
- Performance optimization
- Documentation
- Packaging and distribution

## Success Criteria

### Functional Success
- **Feature Parity**: All bash maestro features implemented
- **Performance**: Comparable or better performance than bash version
- **Usability**: Improved user experience and error messages
- **Reliability**: Reduced error rates and better error recovery

### Technical Success
- **Maintainability**: Clean, well-documented codebase
- **Extensibility**: Plugin architecture for future enhancements
- **Security**: No security vulnerabilities
- **Testing**: Comprehensive test coverage

### Adoption Success
- **Migration**: Successful migration from bash version
- **Documentation**: Complete user and developer documentation
- **Community**: Active user community and contributions
- **Stability**: Production deployments without critical issues

## Future Enhancements

### Short Term
- YAML configuration support
- Enhanced filtering and search capabilities
- Performance optimizations
- Better error messages and help

### Medium Term
- Web-based interface
- Plugin system
- Multi-threaded operations
- Configuration validation schemas

### Long Term
- Support for additional CM tools (Salt, Chef)
- Cloud provider integrations
- Monitoring and alerting
- Configuration drift detection

## Conclusion

This specification provides a comprehensive blueprint for implementing Maestro/Pyestro as a modern, secure, and maintainable configuration management orchestrator. The design emphasizes security, usability, and extensibility while maintaining compatibility with existing workflows and infrastructure.
