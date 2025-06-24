# Migration Guide

Guide for migrating from the original bash Maestro to Python Pyestro.

## Overview

This guide helps you migrate from the original bash-based Maestro to the modern Python-based Pyestro implementation.

## Migration Steps

### 1. Analyze Existing Configuration

First, analyze your current `.maestro` configuration:

```bash
python pyestro.py migrate --analyze /path/to/.maestro
```

### 2. Convert Configuration

Convert your bash configuration to JSON:

```bash
python pyestro.py migrate --convert /path/to/.maestro --output pyestro.json
```

### 3. Validate New Configuration

Validate the converted configuration:

```bash
python pyestro.py config validate
```

### 4. Test Basic Operations

Test that basic operations work:

```bash
python pyestro.py status
python pyestro.py nodes list
```

## Command Mapping

| Original Maestro | Pyestro Equivalent | Notes |
|------------------|-------------------|-------|
| `maestro.sh init` | `python pyestro.py init` | Similar functionality |
| `maestro.sh nodes-list` | `python pyestro.py nodes list` | Enhanced filtering |
| `maestro.sh ansible-module ping` | `python pyestro.py ansible module ping` | Same module support |
| `maestro.sh ansible-play site.yml` | `python pyestro.py ansible playbook site.yml` | Enhanced options |
| `maestro.sh status` | `python pyestro.py status` | More detailed output |

## Configuration Changes

### Bash (.maestro) Format
```bash
maestrodir="/path/to/project"
workdir="./workdir"
toclone["common_inv"]="https://github.com/example/inv.git"
inventorydirs["main"]="./inventory"
```

### JSON (pyestro.json) Format
```json
{
    "maestro": {
        "project_dir": "/path/to/project",
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

## Common Issues

### Issue: Command not found
**Problem**: `python pyestro.py` not working
**Solution**: Ensure you're in the correct directory and Python environment

### Issue: Configuration errors
**Problem**: Invalid configuration after migration
**Solution**: Use `python pyestro.py config validate` to identify issues

### Issue: Missing repositories
**Problem**: Repositories not cloned
**Solution**: Run `python pyestro.py setup` after migration

## Benefits of Migration

- **Better Error Handling**: More informative error messages
- **Enhanced Security**: Input validation and sanitization
- **Improved Performance**: Python optimizations
- **Modern Features**: JSON/YAML configuration, structured logging
- **Maintainability**: Cleaner codebase, unit tests

## Getting Help

- See [Commands](../user-guide/commands.md) for detailed command information
- Check [Configuration](../getting-started/configuration.md) for setup help
- Review [Original Maestro Spec](maestro-spec.md) for comparison
