# Ansible Integration

Advanced Ansible usage with Pyestro.

## Overview

Pyestro provides deep integration with Ansible, allowing you to execute modules, run playbooks, and manage Galaxy roles seamlessly.

## Module Execution

### Basic Module Usage

```bash
# Ping all hosts
python pyestro.py ansible module ping

# Get system facts
python pyestro.py ansible module setup

# Run shell commands
python pyestro.py ansible module shell --args "uptime"
```

### Targeting Specific Hosts

```bash
# Target specific hosts
python pyestro.py ansible module ping --hosts "web*"

# Use complex patterns
python pyestro.py ansible module shell --args "df -h" --hosts "web01,db*"

# Target by class (via reclass)
python pyestro.py ansible module ping --hosts "@webserver"
```

### Module Arguments

```bash
# Service management
python pyestro.py ansible module service --args "name=nginx state=started"

# File operations
python pyestro.py ansible module copy --args "src=/tmp/file dest=/etc/file"

# Package management
python pyestro.py ansible module package --args "name=nginx state=present"
```

## Playbook Management

### Running Playbooks

```bash
# Run a playbook
python pyestro.py ansible playbook site.yml

# Dry-run mode
python pyestro.py ansible playbook site.yml --dry-run

# Target specific hosts
python pyestro.py ansible playbook deploy.yml --hosts "staging"
```

### Playbook Variables

```bash
# Pass variables
python pyestro.py ansible playbook deploy.yml --vars version=1.2.3

# Multiple variables
python pyestro.py ansible playbook site.yml --vars "env=prod debug=false"
```

### Tags and Limits

```bash
# Run specific tags
python pyestro.py ansible playbook site.yml --tags "nginx,ssl"

# Skip tags
python pyestro.py ansible playbook site.yml --skip-tags "slow"

# Limit to specific hosts
python pyestro.py ansible playbook site.yml --limit "web*"
```

### Listing Playbooks

```bash
# List available playbooks
python pyestro.py ansible list-playbooks

# Show playbook details
python pyestro.py ansible list-playbooks --details
```

## Galaxy Role Management

### Installing Roles

```bash
# Install from requirements file
python pyestro.py ansible galaxy-install

# Force reinstall
python pyestro.py ansible galaxy-install --force

# Custom requirements file
python pyestro.py ansible galaxy-install --requirements custom-requirements.yml
```

### Requirements File Format

```yaml
# requirements.yml
- name: geerlingguy.nginx
  version: "2.8.0"

- name: community.mysql
  version: ">=1.0.0"

- src: https://github.com/custom/role.git
  name: custom-role
  version: main
```

## Configuration Generation

Pyestro can generate Ansible configuration files:

```bash
# Generate ansible.cfg
python pyestro.py ansible config-generate
```

Example generated `ansible.cfg`:
```ini
[defaults]
inventory = ./.inventory/reclass
host_key_checking = False
timeout = 60
ansible_managed = Ansible managed. All local changes will be lost!

[ssh_connection]
scp_if_ssh = True
```

## Host Patterns

Pyestro supports various host pattern formats:

### Simple Patterns
```bash
# Single host
--hosts "web01.example.com"

# Wildcard
--hosts "web*"

# Multiple hosts
--hosts "web01,web02,db01"
```

### Reclass Integration
```bash
# All nodes with a class
--hosts "@webserver"

# Nodes with multiple classes
--hosts "@webserver:@nginx"

# Project-based filtering
--hosts "project:ecommerce"
```

### Complex Patterns
```bash
# Intersection
--hosts "webserver:&production"

# Exclusion
--hosts "all:!staging"

# Combination
--hosts "webserver:!web01:&production"
```

## Connectivity Testing

### Basic Connectivity

```bash
# Test all hosts
python pyestro.py ansible ping

# Test specific hosts
python pyestro.py ansible ping --hosts "production"

# Verbose output
python pyestro.py ansible ping --verbose
```

### Advanced Testing

```bash
# Test with timeout
python pyestro.py ansible module ping --args "timeout=30"

# Test with custom user
python pyestro.py ansible module ping --vars ansible_user=deploy

# Test SSH keys
python pyestro.py ansible module shell --args "ssh-add -l"
```

## Troubleshooting

### Common Issues

**Issue**: `Connection timeout`
**Solution**: Check SSH connectivity and firewall rules

**Issue**: `Permission denied`
**Solution**: Verify SSH keys and user permissions

**Issue**: `Host key verification failed`
**Solution**: Add `host_key_checking = False` to ansible.cfg

**Issue**: `Playbook not found`
**Solution**: Check playbook directories in configuration

### Debug Mode

```bash
# Enable verbose output
python pyestro.py --verbose 2 ansible module ping

# Ansible debug mode
python pyestro.py ansible playbook site.yml --vars ansible_verbosity=3
```

## Integration with Reclass

Pyestro automatically integrates Ansible with reclass:

- **Dynamic Inventory**: Automatically generates inventory from reclass
- **Host Variables**: Reclass parameters become Ansible variables
- **Group Variables**: Class-based variable inheritance
- **Facts Integration**: Ansible facts can be stored in reclass

## Best Practices

### Playbook Organization
- Use role-based playbooks
- Implement proper tagging
- Use group_vars and host_vars appropriately

### Variable Management
- Leverage reclass for complex variable hierarchies
- Use Ansible vault for sensitive data
- Implement consistent naming conventions

### Testing
- Always use `--dry-run` for testing
- Test on staging environments first
- Use `--check` mode for validation

For more information, see the [Commands Guide](commands.md).
