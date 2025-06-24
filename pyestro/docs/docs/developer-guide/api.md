# API Reference

Python API reference for Pyestro components.

## Overview

This page provides API documentation for the core Pyestro modules. Use this reference when extending Pyestro or integrating it into other projects.

!!! note "Work in Progress"
    This API reference is being developed. For now, see the source code for detailed implementation details.

## Core Modules

### Configuration Management

#### `pyestro.core.config.MaestroConfig`

Main configuration class for Pyestro.

```python
class MaestroConfig:
    def __init__(self, config_path: Path = None)
    def load_config(self) -> Dict[str, Any]
    def validate(self) -> List[str]
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
```

**Methods:**

- `load_config()` - Load configuration from file
- `validate()` - Validate configuration, returns list of errors
- `get(key, default)` - Get configuration value
- `set(key, value)` - Set configuration value

**Example:**
```python
from pyestro.core.config import MaestroConfig

config = MaestroConfig("pyestro.json")
data = config.load_config()
errors = config.validate()
```

#### `pyestro.core.config.ConfigManager`

Configuration management utilities.

```python
class ConfigManager:
    @staticmethod
    def migrate_from_bash(maestro_path: Path, output_path: Path)
    @staticmethod
    def create_default_config(output_path: Path)
    @staticmethod
    def validate_config_file(config_path: Path) -> List[str]
```

### Input Validation

#### `pyestro.core.validation.InputValidator`

Input validation and sanitization utilities.

```python
class InputValidator:
    @staticmethod
    def sanitize_node_name(name: str) -> str
    @staticmethod
    def validate_url(url: str) -> str
    @staticmethod
    def validate_path(path: str) -> Path
    @staticmethod
    def validate_filter_pattern(pattern: str) -> str
    @staticmethod
    def sanitize_shell_input(input_str: str) -> str
```

**Methods:**

- `sanitize_node_name(name)` - Sanitize node names for reclass
- `validate_url(url)` - Validate and normalize URLs
- `validate_path(path)` - Validate file system paths
- `validate_filter_pattern(pattern)` - Validate search patterns
- `sanitize_shell_input(input)` - Sanitize shell command inputs

**Example:**
```python
from pyestro.core.validation import InputValidator

safe_name = InputValidator.sanitize_node_name("web01.example.com")
safe_url = InputValidator.validate_url("https://github.com/user/repo.git")
```

### Git Operations

#### `pyestro.core.git.GitManager`

Git repository management.

```python
class GitManager:
    def __init__(self, dry_run: bool = True)
    def clone_repository(self, url: str, destination: Path) -> bool
    def pull_repository(self, repo_path: Path) -> bool
    def get_repository_status(self, repo_path: Path) -> Dict[str, Any]
    def clone_repositories(self, repos: Dict[str, str], base_dir: Path) -> Dict[str, bool]
```

**Example:**
```python
from pyestro.core.git import GitManager

git_mgr = GitManager(dry_run=False)
success = git_mgr.clone_repository(
    "https://github.com/user/repo.git", 
    Path("./repo")
)
```

### File Operations

#### `pyestro.core.file_ops.FileManager`

File and directory operations.

```python
class FileManager:
    def __init__(self, dry_run: bool = True)
    def sync_directories(self, source: Path, dest: Path, options: str = "") -> bool
    def merge_directories(self, source: Path, dest: Path, backup: bool = True) -> bool
    def create_backup(self, path: Path) -> Path
```

## Integration Modules

### Reclass Integration

#### `pyestro.parsers.reclass_parser.ReclassManager`

Reclass inventory management.

```python
class ReclassManager:
    def __init__(self, inventory_dir: Path, dry_run: bool = True)
    def get_node_data(self, node_name: str) -> Optional[Dict[str, Any]]
    def get_inventory_data(self) -> Optional[Dict[str, Any]]
    def list_nodes(self) -> List[str]
    def list_classes(self) -> List[str]
    def filter_nodes(self, node_filter: str = None, class_filter: str = None) -> List[str]
    def search_parameter(self, parameter_path: str) -> Dict[str, Any]
    def validate_inventory(self) -> List[str]
```

**Example:**
```python
from pyestro.parsers.reclass_parser import ReclassManager

reclass = ReclassManager(Path("./inventory"))
nodes = reclass.list_nodes()
node_data = reclass.get_node_data("web01.example.com")
```

### Ansible Integration

#### `pyestro.integrations.ansible.AnsibleManager`

Ansible operations management.

```python
class AnsibleManager:
    def __init__(self, dry_run: bool = True)
    def execute_module(self, module: str, module_args: str, host_pattern: str) -> bool
    def run_playbook(self, playbook: str, host_pattern: str, extra_vars: Dict) -> bool
    def list_playbooks(self, playbook_dirs: List[Path]) -> List[str]
    def test_connectivity(self, host_pattern: str) -> Dict[str, bool]
    def install_galaxy_roles(self, requirements_file: Path) -> bool
    def generate_config(self, output_path: Path, inventory_path: Path) -> bool
```

**Example:**
```python
from pyestro.integrations.ansible import AnsibleManager

ansible = AnsibleManager(dry_run=False)
success = ansible.execute_module("ping", "", "all")
result = ansible.test_connectivity("web*")
```

## CLI Components

### Command Handler Base

#### `pyestro.cli.base.CommandHandler`

Base class for CLI command handlers.

```python
class CommandHandler:
    def __init__(self, config: MaestroConfig)
    def execute(self, args: argparse.Namespace) -> int
    def add_arguments(self, parser: argparse.ArgumentParser) -> None
```

### Main CLI Interface

#### `pyestro.cli.main.PyestroCLI`

Main CLI application class.

```python
class PyestroCLI:
    def __init__(self)
    def run(self, args: List[str] = None) -> int
    def register_command(self, name: str, handler: CommandHandler) -> None
```

## Utility Functions

### Logging Utilities

```python
from pyestro.core.config import log_info, log_warning, log_error

log_info("Operation completed successfully")
log_warning("Configuration file not found, using defaults")
log_error("Failed to connect to repository")
```

### Path Utilities

```python
from pyestro.core.file_ops import ensure_directory, safe_path_join

ensure_directory(Path("./workdir"))
safe_path = safe_path_join(base_dir, user_input)
```

## Error Handling

### Exception Classes

#### `pyestro.core.validation.ValidationError`

Raised when input validation fails.

```python
class ValidationError(Exception):
    def __init__(self, message: str, field: str = None)
```

#### `pyestro.core.config.ConfigurationError`

Raised when configuration is invalid.

```python
class ConfigurationError(Exception):
    def __init__(self, message: str, config_path: Path = None)
```

### Error Handling Patterns

```python
from pyestro.core.validation import ValidationError

try:
    validated_input = InputValidator.sanitize_node_name(user_input)
except ValidationError as e:
    log_error(f"Invalid input: {e}")
    return False
```

## Integration Examples

### Custom Command Handler

```python
from pyestro.cli.base import CommandHandler
from pyestro.core.config import MaestroConfig

class CustomCommand(CommandHandler):
    def __init__(self, config: MaestroConfig):
        super().__init__(config)
    
    def add_arguments(self, parser):
        parser.add_argument('--custom-option', help='Custom option')
    
    def execute(self, args):
        # Implement custom logic
        log_info(f"Executing custom command with {args.custom_option}")
        return 0
```

### Custom Integration

```python
from pyestro.core.config import MaestroConfig
from pyestro.core.validation import InputValidator

class CustomIntegration:
    def __init__(self, config: MaestroConfig):
        self.config = config
        self.dry_run = config.get('maestro.dry_run', True)
    
    def execute_custom_operation(self, target: str):
        # Validate input
        safe_target = InputValidator.sanitize_shell_input(target)
        
        # Execute operation
        if self.dry_run:
            log_info(f"DRY RUN: Would execute operation on {safe_target}")
        else:
            # Actual implementation
            pass
```

## Development Guidelines

### Adding New API Methods

1. **Input Validation**: Always validate inputs using `InputValidator`
2. **Error Handling**: Use appropriate exception types
3. **Logging**: Use logging utilities for feedback
4. **Dry-run Support**: Support dry-run mode where applicable
5. **Documentation**: Document with docstrings and type hints

### Type Hints

Use comprehensive type hints for all public APIs:

```python
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

def process_nodes(
    nodes: List[str], 
    filters: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Process node list with optional filters."""
    pass
```

### Testing APIs

```python
import pytest
from pyestro.core.config import MaestroConfig

def test_config_loading():
    config = MaestroConfig("test_config.json")
    data = config.load_config()
    assert isinstance(data, dict)
    
def test_input_validation():
    from pyestro.core.validation import InputValidator, ValidationError
    
    with pytest.raises(ValidationError):
        InputValidator.sanitize_node_name("invalid../node")
```

For more detailed implementation examples, see the source code in the respective modules.
