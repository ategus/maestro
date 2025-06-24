# Reclass Integration

Working with reclass in Pyestro.

## Overview

Pyestro uses reclass as its primary metadata backend, providing a powerful knowledge base for configuration management.

## Basic Usage

### Listing Nodes

```bash
# List all nodes
python pyestro.py nodes list

# Filter by pattern
python pyestro.py nodes list --filter "web*"

# Filter by class
python pyestro.py nodes list --class webserver
```

### Node Information

```bash
# Show node details
python pyestro.py nodes show web01.example.com

# Show in different formats
python pyestro.py nodes show web01.example.com --format json
python pyestro.py nodes show web01.example.com --format yaml
```

### Class Management

```bash
# List all classes
python pyestro.py classes list

# Show class details
python pyestro.py classes show webserver

# Find nodes using a class
python pyestro.py nodes list --class apache
```

## Searching Parameters

```bash
# Search for specific parameters
python pyestro.py search app:nginx:version

# Search with wildcards
python pyestro.py search "*:ssl:*"

# Complex parameter paths
python pyestro.py search host:network:interfaces:eth0:ip
```

## Reclass Structure

Pyestro expects a standard reclass directory structure:

```
inventory/
├── classes/
│   ├── admin/
│   ├── location/
│   ├── project/
│   ├── role/
│   ├── service/
│   └── app/
│       ├── apache/
│       ├── nginx/
│       └── ...
└── nodes/
    ├── project1/
    │   ├── web01.example.com.yml
    │   └── db01.example.com.yml
    └── project2/
        └── ...
```

## Configuration

Configure reclass in your `pyestro.json`:

```json
{
    "inventory": {
        "main": "./inventory",
        "secondary": "./inventory2"
    }
}
```

## Advanced Features

### Parameter Resolution
Pyestro resolves parameters through the reclass hierarchy, showing final merged values.

### Class Inheritance
View the complete class inheritance chain for any node.

### Validation
Built-in validation ensures your reclass inventory is syntactically correct.

## Troubleshooting

### Common Issues

**Issue**: `reclass executable not found`
**Solution**: Install reclass: `pip install reclass`

**Issue**: `Inventory directory does not exist`
**Solution**: Check your inventory path in `pyestro.json`

**Issue**: `Failed to load inventory data`
**Solution**: Validate your reclass syntax with `reclass --inventory`

For more information, see the [Commands Guide](commands.md).
