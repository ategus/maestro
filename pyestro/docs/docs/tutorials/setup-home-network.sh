#!/bin/bash
# Home Network Pyestro Setup Script
# Run this script to quickly bootstrap your home automation project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if Python is installed
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if pip is available
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check if git is available
    if command -v git &> /dev/null; then
        print_success "git found"
    else
        print_error "git is required but not installed"
        exit 1
    fi
    
    # Check if ssh is available
    if command -v ssh &> /dev/null; then
        print_success "ssh found"
    else
        print_warning "ssh not found - you'll need it for device management"
    fi
}

# Setup project directory
setup_project() {
    print_header "Setting Up Project Directory"
    
    echo "Enter your project directory name (default: home-automation):"
    read -r PROJECT_NAME
    PROJECT_NAME=${PROJECT_NAME:-home-automation}
    
    if [ -d "$PROJECT_NAME" ]; then
        print_warning "Directory $PROJECT_NAME already exists"
        echo "Do you want to continue and potentially overwrite files? (y/N):"
        read -r CONTINUE
        if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
            print_info "Setup cancelled"
            exit 0
        fi
    fi
    
    mkdir -p "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    print_success "Created project directory: $PROJECT_NAME"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Created virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Activated virtual environment"
    
    # Install Ansible and other requirements
    pip install --upgrade pip
    pip install ansible
    pip install jinja2
    pip install netaddr
    pip install pyyaml
    pip install requests
    
    print_success "Installed Python dependencies"
}

# Create directory structure
create_structure() {
    print_header "Creating Directory Structure"
    
    # Create main directories
    mkdir -p inventory/classes/{hardware,services,network,security}
    mkdir -p inventory/nodes/{homeassistant,nas,monitoring,network}
    mkdir -p playbooks
    mkdir -p roles
    mkdir -p group_vars
    mkdir -p host_vars
    mkdir -p files
    mkdir -p templates
    mkdir -p scripts
    mkdir -p backups
    
    print_success "Created directory structure"
}

# Copy template files
copy_templates() {
    print_header "Setting Up Configuration Templates"
    
    # Create basic pyestro.yml from template
    cat > pyestro.yml << 'EOF'
maestro:
  project_dir: .
  work_dir: ./workdir
  dry_run: true
  verbose: 2

inventory:
  backend: reclass
  sources:
    main: ./inventory

playbooks:
  main: ./playbooks
  roles: ./roles

ansible:
  timeout: 120
  host_key_checking: false
  gathering: smart

network:
  domain: home.local
  management_subnet: 192.168.1.0/24
EOF
    
    print_success "Created pyestro.yml configuration"
    
    # Create basic inventory structure
    cat > inventory/classes/network/base.yml << 'EOF'
parameters:
  network:
    domain: home.local
    dns_servers:
      - 192.168.1.1
      - 8.8.8.8
    ntp_servers:
      - pool.ntp.org
  
  users:
    admin:
      name: admin
      groups: [sudo]
      shell: /bin/bash
  
  packages:
    common:
      - curl
      - wget
      - htop
      - vim
      - git
EOF
    
    # Create hardware classes
    cat > inventory/classes/hardware/raspberry_pi.yml << 'EOF'
classes:
  - network.base

parameters:
  hardware:
    type: raspberry_pi
    architecture: arm64
    
  system:
    timezone: UTC
    
  monitoring:
    node_exporter: true
EOF
    
    cat > inventory/classes/hardware/nas_server.yml << 'EOF'
classes:
  - network.base

parameters:
  hardware:
    type: nas_server
    architecture: x86_64
    
  storage:
    zfs_enabled: true
    smart_monitoring: true
    
  services:
    smb_enabled: true
    nfs_enabled: true
EOF
    
    # Create service classes
    cat > inventory/classes/services/home_assistant.yml << 'EOF'
classes:
  - hardware.raspberry_pi

parameters:
  homeassistant:
    version: latest
    port: 8123
    config_path: /usr/share/hassio/homeassistant
    
  services:
    - homeassistant
    - mosquitto
EOF
    
    cat > inventory/classes/services/nas_services.yml << 'EOF'
classes:
  - hardware.nas_server

parameters:
  nas:
    web_port: 443
    
  shares:
    media:
      path: /mnt/tank/media
      type: smb
      
    backups:
      path: /mnt/tank/backups
      type: nfs
EOF
    
    print_success "Created inventory class templates"
}

# Create example nodes
create_example_nodes() {
    print_header "Creating Example Node Configurations"
    
    # Home Assistant node
    cat > inventory/nodes/homeassistant/ha-main.yml << 'EOF'
classes:
  - services.home_assistant

parameters:
  networking:
    ip_address: 192.168.1.100
    hostname: ha-main
    
  homeassistant:
    device_name: "Home Assistant Main"
EOF
    
    # NAS node
    cat > inventory/nodes/nas/nas-main.yml << 'EOF'
classes:
  - services.nas_services

parameters:
  networking:
    ip_address: 192.168.1.200
    hostname: nas-main
    
  storage:
    pools:
      tank:
        devices:
          - /dev/sda
          - /dev/sdb
        raid_level: mirror
EOF
    
    print_success "Created example node configurations"
}

# Create basic playbooks
create_playbooks() {
    print_header "Creating Basic Playbooks"
    
    # Main site playbook
    cat > playbooks/site.yml << 'EOF'
---
- name: Home Network Infrastructure
  hosts: all
  become: yes
  gather_facts: yes
  
  tasks:
    - name: Update package cache
      package:
        update_cache: yes
      when: ansible_os_family in ['Debian', 'RedHat']
    
    - name: Install common packages
      package:
        name: "{{ packages.common }}"
        state: present
      when: packages.common is defined

- name: Home Assistant Setup
  hosts: homeassistant
  become: yes
  
  tasks:
    - name: Ensure Home Assistant is running
      systemd:
        name: hassio-supervisor
        state: started
        enabled: yes
      ignore_errors: yes

- name: NAS Server Setup  
  hosts: nas
  become: yes
  
  tasks:
    - name: Install ZFS utilities
      package:
        name: zfsutils-linux
        state: present
      when: storage.zfs_enabled | default(false)
EOF
    
    # Health check playbook
    cat > playbooks/health-check.yml << 'EOF'
---
- name: Health Check All Devices
  hosts: all
  gather_facts: yes
  
  tasks:
    - name: Check disk usage
      shell: df -h
      register: disk_usage
      
    - name: Display disk usage
      debug:
        var: disk_usage.stdout_lines
        
    - name: Check memory usage
      shell: free -h
      register: memory_usage
      
    - name: Display memory usage
      debug:
        var: memory_usage.stdout_lines
EOF
    
    print_success "Created basic playbooks"
}

# Create helper scripts
create_scripts() {
    print_header "Creating Helper Scripts"
    
    # Create activation script
    cat > activate.sh << 'EOF'
#!/bin/bash
# Activate the Python virtual environment and set up environment

source venv/bin/activate

# Add current directory to Python path for Pyestro
export PYTHONPATH="$PWD:$PYTHONPATH"

# Set default Pyestro config
export PYESTRO_CONFIG="$PWD/pyestro.yml"

echo "🏠 Home Automation environment activated!"
echo "📋 Project directory: $PWD"
echo "🔧 Pyestro config: $PYESTRO_CONFIG"
echo ""
echo "Quick commands:"
echo "  python pyestro.py status          # Check all devices"
echo "  python pyestro.py nodes list      # List all nodes"
echo "  python pyestro.py config validate # Validate configuration"
echo ""
echo "To deactivate: deactivate"
EOF
    
    chmod +x activate.sh
    
    # Create quick status script
    cat > scripts/quick-status.sh << 'EOF'
#!/bin/bash
# Quick status check for home network

echo "🏠 Home Network Status Check"
echo "=========================="

# Check if devices are reachable
echo ""
echo "📡 Network Connectivity:"
ping -c 1 192.168.1.100 >/dev/null 2>&1 && echo "✅ Home Assistant (192.168.1.100)" || echo "❌ Home Assistant (192.168.1.100)"
ping -c 1 192.168.1.200 >/dev/null 2>&1 && echo "✅ NAS Server (192.168.1.200)" || echo "❌ NAS Server (192.168.1.200)"

# Check services if Pyestro is available
if command -v python &> /dev/null && [ -f "pyestro.py" ]; then
    echo ""
    echo "🔧 Pyestro Status:"
    python pyestro.py status 2>/dev/null || echo "⚠️  Pyestro not configured yet"
fi

echo ""
echo "💡 To get started:"
echo "   source activate.sh"
echo "   python pyestro.py config validate"
EOF
    
    chmod +x scripts/quick-status.sh
    
    print_success "Created helper scripts"
}

# Create README
create_readme() {
    print_header "Creating Documentation"
    
    cat > README.md << 'EOF'
# Home Network Automation with Pyestro

This project uses Pyestro to automate the management of home network infrastructure including:

- 🏠 Home Assistant on Raspberry Pi
- 💾 NAS Server with TrueNAS/OpenMediaVault  
- 🔐 Security and monitoring setup
- 📋 Automated backups and maintenance

## Quick Start

1. **Activate the environment:**
   ```bash
   source activate.sh
   ```

2. **Validate your configuration:**
   ```bash
   python pyestro.py config validate
   ```

3. **Check device connectivity:**
   ```bash
   python pyestro.py nodes ping
   ```

4. **Run initial setup (dry-run):**
   ```bash
   python pyestro.py setup --dry-run
   ```

5. **Run actual setup:**
   ```bash
   python pyestro.py setup
   ```

## Configuration

Edit `pyestro.yml` to match your network setup:

- Update IP addresses in `inventory/nodes/`
- Modify hardware specifications in `inventory/classes/hardware/`
- Customize services in `inventory/classes/services/`

## Daily Operations

```bash
# Check status of all devices
python pyestro.py status

# Run health checks
python pyestro.py ansible-playbook playbooks/health-check.yml

# Update configurations
python pyestro.py ansible-playbook playbooks/site.yml

# Quick network status
./scripts/quick-status.sh
```

## Directory Structure

```
├── pyestro.yml              # Main Pyestro configuration
├── inventory/               # Device and service definitions
│   ├── classes/            # Reusable configuration classes
│   └── nodes/              # Individual device configs
├── playbooks/              # Ansible automation
├── scripts/                # Helper scripts
└── backups/                # Local backup storage
```

## Customization

1. **Add new devices:** Create node files in `inventory/nodes/`
2. **Add services:** Create service classes in `inventory/classes/services/`
3. **Custom automation:** Add playbooks in `playbooks/`
4. **Monitoring:** Configure alerts and health checks

## Security Notes

- All operations run in dry-run mode by default
- SSH keys should be properly configured
- Firewall rules are applied automatically
- Regular backups are scheduled

## Troubleshooting

- **Connection issues:** Check `./scripts/quick-status.sh`
- **Configuration errors:** Run `python pyestro.py config validate`
- **Service problems:** Check logs with `python pyestro.py ansible <host> -m shell -a "journalctl -xe"`

For detailed tutorials and documentation, see the Pyestro documentation.
EOF
    
    print_success "Created README.md"
    
    # Create .gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# Pyestro
workdir/
.ansible-galaxy-roles/
*.retry

# Sensitive files
vault_pass.txt
*.pem
*.key
id_rsa*

# Local files
backups/
logs/
.DS_Store
.vscode/
*.swp
*.swo
EOF
    
    print_success "Created .gitignore"
}

# Final setup instructions
show_final_instructions() {
    print_header "Setup Complete!"
    
    print_success "Your home automation project has been set up successfully!"
    echo ""
    print_info "Next steps:"
    echo "1. Edit the IP addresses in inventory/nodes/ to match your devices"
    echo "2. Configure SSH access to your Raspberry Pi and NAS"
    echo "3. Run: source activate.sh"
    echo "4. Run: python pyestro.py config validate"
    echo "5. Run: ./scripts/quick-status.sh to test connectivity"
    echo ""
    print_info "Important files to customize:"
    echo "- pyestro.yml (main configuration)"
    echo "- inventory/nodes/homeassistant/ha-main.yml (Home Assistant config)"
    echo "- inventory/nodes/nas/nas-main.yml (NAS server config)"
    echo ""
    print_warning "Remember: Always test with --dry-run first!"
    echo ""
    print_info "For detailed instructions, see the tutorial in the Pyestro documentation."
}

# Main execution
main() {
    print_header "Pyestro Home Network Setup"
    echo "This script will set up a complete home automation project structure"
    echo ""
    
    check_prerequisites
    setup_project
    install_dependencies
    create_structure
    copy_templates
    create_example_nodes
    create_playbooks
    create_scripts
    create_readme
    show_final_instructions
}

# Run main function
main "$@"
