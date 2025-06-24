# Architecture

Pyestro architecture and design principles.

## Overview

Pyestro follows a modular, three-layer architecture that provides clear separation of concerns while maintaining flexibility and extensibility.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                          │
├─────────────────────────────────────────────────────────────┤
│ CLI Interface (pyestro/cli/main.py)                        │
│ ├── Command Parsing                                        │
│ ├── Option Validation                                      │
│ └── Output Formatting                                      │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   CORE LAYER                               │
├─────────────────────────────────────────────────────────────┤
│ Configuration Management (pyestro/core/config.py)          │
│ ├── JSON/YAML Configuration Loading                        │
│ ├── Environment Variable Processing                        │
│ └── Configuration Validation                               │
│                                                             │
│ Input Validation (pyestro/core/validation.py)              │
│ ├── Security Input Sanitization                            │
│ ├── Parameter Validation                                   │
│ └── Error Handling                                         │
│                                                             │
│ File Operations (pyestro/core/file_ops.py)                 │
│ ├── Rsync Integration                                       │
│ ├── File Synchronization                                   │
│ └── Backup Management                                       │
│                                                             │
│ Git Operations (pyestro/core/git.py)                       │
│ ├── Repository Management                                   │
│ ├── Clone/Pull Operations                                   │
│ └── Status Checking                                         │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                INTEGRATION LAYER                           │
├─────────────────────────────────────────────────────────────┤
│ Reclass Parser (pyestro/parsers/reclass_parser.py)         │
│ ├── JSON Parsing                                           │
│ ├── Node/Class Management                                  │
│ ├── Parameter Resolution                                    │
│ └── Inventory Validation                                    │
│                                                             │
│ Ansible Integration (pyestro/integrations/ansible.py)      │
│ ├── Module Execution                                        │
│ ├── Playbook Management                                     │
│ ├── Galaxy Role Management                                  │
│ └── Configuration Generation                                │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                EXTERNAL SYSTEMS                            │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │   Reclass   │ │   Ansible   │ │     Git     │            │
│ │ (Metadata)  │ │    (CM)     │ │ (Repos)     │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
│                               │                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │   Target    │ │  File       │ │  Network    │            │
│ │   Hosts     │ │  Systems    │ │  Resources  │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Core Design Principles

### 1. Separation of Concerns
- **CLI Layer**: User interface and command parsing
- **Core Layer**: Business logic and operations
- **Integration Layer**: External tool interfaces
- **External Systems**: Managed resources

### 2. Security First
- **Input Validation**: All inputs validated and sanitized
- **Path Traversal Protection**: Secure file operations
- **Command Injection Prevention**: Safe external command execution
- **Privilege Management**: Controlled privilege escalation

### 3. Error Handling
- **Graceful Degradation**: Continue where possible
- **Informative Messages**: Clear, actionable error messages
- **Logging**: Comprehensive logging for debugging
- **Recovery**: Support for recovery operations

### 4. Modularity
- **Plugin Architecture**: Extensible design
- **Interface Contracts**: Clear API boundaries
- **Dependency Injection**: Testable components
- **Configuration Driven**: Behavior controlled by configuration

## Component Details

### CLI Interface (`pyestro/cli/main.py`)

The command-line interface provides:
- Hierarchical command structure
- Option parsing and validation
- Output formatting (JSON, YAML, table)
- Interactive prompts and confirmations

```python
# Command structure example
python pyestro.py [global-options] <command> [subcommand] [options] [args]
```

### Configuration Management (`pyestro/core/config.py`)

Features:
- JSON primary format, YAML support planned
- Environment variable overrides
- Configuration validation
- Migration from bash .maestro files

```python
class MaestroConfig:
    def __init__(self, config_path: Path)
    def load_config(self) -> Dict[str, Any]
    def validate(self) -> List[str]
    def migrate_from_bash(self, maestro_path: Path)
```

### Input Validation (`pyestro/core/validation.py`)

Security-focused validation:
- URL validation and sanitization
- Hostname validation
- Path traversal prevention
- Shell command sanitization

```python
class InputValidator:
    @staticmethod
    def sanitize_node_name(name: str) -> str
    @staticmethod
    def validate_url(url: str) -> str
    @staticmethod
    def validate_path(path: str) -> Path
```

### Reclass Integration (`pyestro/parsers/reclass_parser.py`)

Comprehensive reclass support:
- JSON parsing of reclass output
- Node and class management
- Parameter search and filtering
- Inventory validation

```python
class ReclassManager:
    def get_node_data(self, node_name: str) -> Optional[Dict[str, Any]]
    def get_inventory_data(self) -> Optional[Dict[str, Any]]
    def filter_nodes(self, filters: Dict[str, str]) -> List[str]
```

### Ansible Integration (`pyestro/integrations/ansible.py`)

Full Ansible support:
- Module execution with parameter validation
- Playbook discovery and execution
- Galaxy role management
- Dynamic host pattern generation

```python
class AnsibleManager:
    def execute_module(self, module: str, args: str, hosts: str)
    def run_playbook(self, playbook: str, hosts: str, vars: Dict)
    def install_galaxy_roles(self, requirements: Path)
```

## Data Flow

### Typical Operation Flow

1. **Command Parsing**
   ```
   CLI → ArgumentParser → Command Dispatcher
   ```

2. **Configuration Loading**
   ```
   Config File → Environment Variables → Validation → Runtime Config
   ```

3. **Input Validation**
   ```
   User Input → Sanitization → Security Checks → Validated Parameters
   ```

4. **External Tool Integration**
   ```
   Validated Parameters → Tool Execution → Output Processing → User Response
   ```

5. **Error Handling**
   ```
   Errors → Logging → User-Friendly Messages → Recovery Options
   ```

## Extension Points

### Adding New Commands

1. Create command handler in `pyestro/cli/`
2. Register in main command dispatcher
3. Add validation rules
4. Implement business logic
5. Add tests

### Adding New Integrations

1. Create integration module in `pyestro/integrations/`
2. Implement standard interface
3. Add configuration schema
4. Add input validation
5. Add error handling

### Adding New Parsers

1. Create parser module in `pyestro/parsers/`
2. Implement parser interface
3. Add data validation
4. Add caching support
5. Add tests

## Performance Considerations

### Caching Strategy
- **Reclass Data**: Cache inventory data to avoid repeated queries
- **Configuration**: Cache validated configuration
- **Repository Status**: Cache git status information

### Parallel Operations
- **Repository Operations**: Parallel git operations where safe
- **Ansible Execution**: Support for parallel module execution
- **File Operations**: Parallel file synchronization

### Memory Management
- **Streaming**: Stream large outputs rather than loading in memory
- **Lazy Loading**: Load data only when needed
- **Resource Cleanup**: Proper cleanup of resources

## Testing Architecture

### Unit Tests
- **Isolated Testing**: Each component tested in isolation
- **Mock Dependencies**: External dependencies mocked
- **Input Validation**: Comprehensive input validation testing
- **Error Conditions**: Error condition testing

### Integration Tests
- **End-to-End**: Complete workflow testing
- **External Tools**: Testing with real external tools
- **Configuration**: Various configuration scenarios
- **Error Recovery**: Error recovery testing

### Performance Tests
- **Large Inventories**: Testing with large inventories (1000+ nodes)
- **Concurrent Operations**: Multi-user scenarios
- **Memory Usage**: Memory leak detection
- **Response Times**: Performance benchmarking

## Security Architecture

### Input Validation
- **Sanitization**: All inputs sanitized before processing
- **Validation**: Type and format validation
- **Injection Prevention**: SQL/Command injection prevention
- **Path Traversal**: Directory traversal prevention

### Privilege Management
- **Least Privilege**: Run with minimum required privileges
- **Sudo Integration**: Controlled privilege escalation
- **User Context**: Operations in user context where possible
- **Audit Trail**: Logging of privileged operations

### Secrets Management
- **No Hardcoded Secrets**: No secrets in code or configuration
- **Environment Variables**: Sensitive data via environment variables
- **Secure Storage**: Integration with secure storage systems
- **Logging Safety**: Prevent secrets in logs

## Future Architecture Enhancements

### Planned Improvements
- **Plugin System**: Dynamic plugin loading
- **Web Interface**: REST API and web UI
- **Database Backend**: Optional database for large inventories
- **Distributed Operations**: Multi-node orchestration
- **Event System**: Event-driven architecture
- **Metrics Collection**: Performance and usage metrics

### Scalability Improvements
- **Horizontal Scaling**: Multi-instance support
- **Load Balancing**: Request load balancing
- **Caching Layers**: Multi-level caching
- **Async Operations**: Asynchronous operation support

This architecture provides a solid foundation for the current Pyestro implementation while allowing for future enhancements and scalability improvements.
