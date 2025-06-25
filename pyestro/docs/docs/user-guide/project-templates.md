# Project Templates

Pyestro provides a powerful template system for quickly creating new projects with pre-configured structures and best practices.

## Overview

The template system allows you to:
- **Rapid Project Setup**: Get from zero to working project in minutes
- **Best Practices**: Templates include proven configurations and structures
- **Customization**: Templates support variables for customization
- **Consistency**: Standardized project layouts across teams

## Quick Start

### Create a Project

```bash
# Interactive creation (recommended for beginners)
python pyestro.py create --wizard

# Direct creation
python pyestro.py create <template-name> <project-name>

# List available templates
python pyestro.py create --list
```

### Example

```bash
# Create a home automation project
python pyestro.py create home-network my-smart-home

# Create with custom settings
python pyestro.py create home-network my-home \
  --var=network_name=mynetwork \
  --var=domain_name=mynetwork.local \
  --var=has_homeassistant=y \
  --var=has_nas=y
```

## Available Templates

### Basic Template

**Purpose**: Minimal Pyestro project for getting started quickly.

**Use Cases**:
- Learning Pyestro fundamentals
- Simple infrastructure automation
- Custom project bases

**What's Included**:
- Basic `pyestro.json` configuration
- Simple inventory structure (`inventory/classes/`, `inventory/nodes/`)
- Playbook directory (`playbooks/`)
- Documentation and `.gitignore`

**Variables**:
- `work_dir`: Working directory name (default: `workdir`)
- `inventory_repo`: Optional inventory repository URL
- `playbooks_repo`: Optional playbooks repository URL
- `enable_ansible`: Enable Ansible integration (default: `y`)

**Example**:
```bash
python pyestro.py create basic my-project \
  --var=work_dir=custom-workdir \
  --var=enable_ansible=y
```

### Home Network Template

**Purpose**: Complete home automation and network management solution.

**Use Cases**:
- Home automation with Home Assistant
- NAS and media server management
- Network monitoring and security
- IoT device management

**What's Included**:
- Comprehensive project structure
- Home Assistant configuration classes
- NAS server setup
- Network monitoring setup
- Security configurations
- Setup scripts and documentation

**Variables**:
- `network_name`: Home network name (default: `home`)
- `domain_name`: Local domain (default: `home.local`)
- `network_subnet`: Network subnet (default: `192.168.1.0/24`)
- `has_homeassistant`: Include Home Assistant (default: `y`)
- `has_nas`: Include NAS server (default: `y`)
- `has_monitoring`: Include monitoring (default: `y`)
- `backup_location`: Backup directory (default: `./backups`)

**Example**:
```bash
python pyestro.py create home-network my-smart-home \
  --var=network_name=smarthome \
  --var=domain_name=smarthome.local \
  --var=network_subnet=10.0.1.0/24 \
  --var=has_homeassistant=y \
  --var=has_nas=y \
  --var=has_monitoring=y
```

**Generated Structure**:
```
my-smart-home/
├── pyestro.json              # Main configuration
├── README.md                 # Comprehensive documentation
├── setup.sh                  # Setup script
├── inventory/                # Device and service definitions
│   ├── classes/
│   │   ├── hardware/         # Hardware-specific configs
│   │   ├── services/         # Service definitions
│   │   ├── network/          # Network configurations
│   │   └── security/         # Security policies
│   └── nodes/                # Individual device configs
├── playbooks/                # Ansible automation
│   └── roles/                # Custom roles
├── scripts/                  # Helper scripts
└── backups/                  # Backup storage
```

### PostgreSQL Template

**Purpose**: Production-ready PostgreSQL database infrastructure with automated backup solution.

**Use Cases**:
- Application database backend
- Data warehousing and analytics
- High-availability database clusters
- Database backup and disaster recovery

**What's Included**:
- Primary PostgreSQL server configuration
- Backup server with automated backup solution
- Streaming replication setup
- SSL/TLS encryption configuration
- Monitoring and alerting setup
- Database management scripts

**Variables**:
- `primary_db_ip`: Primary database server IP (default: `192.168.1.120`)
- `backup_server_ip`: Backup server IP (default: `192.168.1.121`)
- `db_name`: Database name (default: `myapp`)
- `db_user`: Database user (default: `myapp_user`)
- `postgresql_version`: PostgreSQL version (default: `14`)
- `enable_replication`: Enable streaming replication (default: `y`)
- `backup_retention_days`: Backup retention period (default: `30`)
- `enable_ssl`: Enable SSL/TLS (default: `y`)
- `max_connections`: Maximum connections (default: `200`)
- `shared_buffers`: Shared buffers size (default: `256MB`)

**Example**:
```bash
python pyestro.py create postgres my-database \
  --var=primary_db_ip=10.0.1.120 \
  --var=backup_server_ip=10.0.1.121 \
  --var=db_name=production_db \
  --var=db_user=app_user \
  --var=postgresql_version=14 \
  --var=enable_replication=y \
  --var=backup_retention_days=30
```

**Generated Structure**:
```
my-database/
├── pyestro.json              # Main configuration
├── README.md                 # Database documentation
├── setup.sh                  # Setup script
├── inventory/                # Server definitions
│   ├── classes/
│   │   ├── hardware/         # Server hardware configs
│   │   ├── services/         # PostgreSQL configs
│   │   ├── network/          # Network configurations
│   │   ├── security/         # Security policies
│   │   └── monitoring/       # Monitoring configs
│   └── nodes/
│       ├── primary-db.yml    # Primary database server
│       └── backup-server.yml # Backup server
├── playbooks/                # Ansible automation
│   ├── site.yml              # Main deployment
│   └── roles/                # PostgreSQL roles
├── scripts/                  # Management scripts
│   ├── backup_postgresql.sh  # Backup automation
│   ├── monitoring.sh         # Health checks
│   └── restore_postgresql.sh # Restore procedures
└── backups/                  # Local backup storage
```

## Interactive Wizard

The interactive wizard guides you through project creation:

```bash
python pyestro.py create --wizard
```

The wizard will:
1. Show available templates with descriptions
2. Help you select the right template
3. Prompt for project name and location
4. Collect template-specific variables
5. Show a summary before creation
6. Create the project with your settings

## Template Variables

Templates support variables for customization:

### Setting Variables

```bash
# Via command line
python pyestro.py create template-name project-name --var=key=value

# Multiple variables
python pyestro.py create home-network my-home \
  --var=network_name=home \
  --var=domain_name=home.local \
  --var=has_nas=y
```

### Variable Types

Templates can define different types of variables:
- **String**: Text values (names, URLs, paths)
- **Boolean**: Yes/no choices (y/n)
- **Numeric**: Numbers (ports, timeouts)
- **Choice**: Predefined options

### Default Values

All template variables have sensible defaults, so you can create projects without specifying any variables.

## Project Structure

All templates create a consistent base structure:

```
project-name/
├── pyestro.json          # Main configuration
├── README.md             # Project documentation
├── .gitignore           # Git ignore patterns
├── workdir/             # Working directory
├── inventory/           # Reclass inventory
│   ├── classes/         # Reclass classes
│   └── nodes/           # Node configurations
└── playbooks/           # Ansible playbooks
```

Templates may add additional directories and files based on their purpose.

## Advanced Usage

### Custom Target Directory

```bash
# Create in specific directory
python pyestro.py create basic my-project --dir=/path/to/projects/my-project
```

### Dry Run Mode

```bash
# Preview what would be created
python pyestro.py create basic my-project --dry-run
```

### Template Information

```bash
# List templates with descriptions
python pyestro.py create --list
```

## Best Practices

### Choosing Templates

- **Basic**: Start here if you're new to Pyestro or building custom automation
- **Home Network**: Perfect for home automation projects

### After Creation

1. **Review Configuration**: Check `pyestro.json` for your environment
2. **Validate Setup**: Run `python pyestro.py config validate`
3. **Initialize Environment**: Run `python pyestro.py setup`
4. **Customize Inventory**: Add your actual devices and services
5. **Test Connectivity**: Run `python pyestro.py status`

### Project Organization

- Keep templates as starting points, not final solutions
- Customize inventory for your specific environment
- Add your own playbooks and roles as needed
- Document customizations in your project README

## Next Steps

After creating a project with templates:

1. **[Configure Your Project](configuration.md)** - Customize settings
2. **[Manage Inventory](../reference/reclass.md)** - Add devices and services
3. **[Run Playbooks](commands.md#ansible-playbook)** - Deploy configurations
4. **[Monitor Status](commands.md#status)** - Check system health

## Troubleshooting

### Template Not Found
```bash
# Check available templates
python pyestro.py create --list
```

### Invalid Project Name
Project names must:
- Contain only letters, numbers, hyphens, and underscores
- Not start with dots or hyphens
- Be under 100 characters

### Variable Errors
Check template documentation for required variable formats and valid values.

For more help, see the [Troubleshooting Guide](../troubleshooting.md).