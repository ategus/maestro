# Legacy Maestro Home Network Tutorial

Learn how to use the original bash-based Maestro to manage your home infrastructure including Raspberry Pi devices running Home Assistant and a NAS server.

!!! info "Legacy System"
    This tutorial covers the original bash-based Maestro system. For new projects, consider using [Pyestro](../tutorials/home-network-setup.md) which provides the same functionality with modern Python architecture.

## Overview

This tutorial demonstrates using the original Maestro script to manage:

- **Raspberry Pi 4** running Home Assistant OS
- **NAS Server** running TrueNAS SCALE or OpenMediaVault  
- **Network Services** like Pi-hole, Nginx proxy, monitoring
- **Backup and Maintenance** automation

## Prerequisites

### Hardware Setup
- Raspberry Pi 4 (4GB+ RAM recommended) with Home Assistant OS
- NAS server (dedicated hardware or repurposed PC) with TrueNAS SCALE/OMV
- Network switch/router with SSH access capability
- Management machine (laptop/desktop) running Linux/macOS

### Software Requirements
- Bash shell (4.0+)
- Git
- SSH client
- Ansible (2.9+)
- Reclass
- rsync

### Installation

```bash
# Clone the original Maestro repository
git clone https://github.com/inofix/maestro.git
cd maestro

# Make the script executable
chmod +x maestro.sh

# Install dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install ansible reclass rsync git

# Install dependencies (macOS with Homebrew)
brew install ansible reclass rsync git
```

## Project Structure

```
home-automation/
├── .maestro                    # Main configuration file
├── maestro.sh                  # Maestro script (symlinked)
├── inventory/                  # Reclass inventory
│   ├── classes/
│   │   ├── hardware/          # Hardware-specific configs
│   │   ├── services/          # Service definitions
│   │   ├── network/           # Network configurations
│   │   └── security/          # Security policies
│   └── nodes/                 # Individual device configs
├── common_playbooks/          # Downloaded playbooks
├── common_inv/                # Downloaded common inventory
└── workdir/                   # Working directory (created automatically)
```

## Step 1: Initial Maestro Setup

### Create Project Directory

```bash
mkdir ~/home-automation
cd ~/home-automation
```

### Create Configuration File

Create `.maestro` configuration file:

```bash
cat > .maestro << 'EOF'
# Maestro Configuration for Home Network Automation

# Project directory (where this file is located)
maestrodir="$(pwd)"

# Working directory for temporary files
workdir="./workdir"

# Git repositories to clone
declare -A toclone
toclone["maestro"]="https://github.com/inofix/maestro.git"
toclone["common_inv"]="https://github.com/inofix/common-inv.git"
toclone["common_playbooks"]="https://github.com/zwischenloesung/common-playbooks.git"

# Inventory directories (reclass)
declare -A inventorydirs
inventorydirs["main"]="./inventory"
inventorydirs["common"]="./common_inv"

# Playbook directories
declare -A playbookdirs
playbookdirs["common_playbooks"]="./common_playbooks"
playbookdirs["site_playbooks"]="./playbooks"

# Ansible configuration
ansible_managed="Ansible managed by Maestro. All local changes will be lost!"
ansible_timeout="120"
ansible_host_key_checking="False"
ansible_gathering="smart"

# SSH configuration for home network
ansible_ssh_args="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
ansible_ssh_retries="3"

# Rsync options
rsync_opts="-a -m --exclude=.keep --exclude=*.tmp"

# Network configuration
network_domain="home.local"
network_dns_servers="192.168.1.1,8.8.8.8"

# Home Assistant configuration
homeassistant_ip="192.168.1.100"
homeassistant_user="homeuser"
homeassistant_config_path="/usr/share/hassio/homeassistant"

# NAS configuration
nas_ip="192.168.1.200"
nas_user="root"
nas_backup_path="/mnt/tank/backups"

# Security settings
ufw_enabled="true"
fail2ban_enabled="true"

# Backup settings
backup_enabled="true"
backup_schedule="0 2 * * *"  # Daily at 2 AM
backup_retention="30"        # Keep 30 days

# Development/testing
dry_run="true"              # Safe mode by default
force_mode="false"
verbose_level="2"           # 0=quiet, 1=normal, 2=verbose, 3=debug
EOF
```

### Initialize Maestro

```bash
# Create symlink to maestro script (after cloning)
ln -s maestro/maestro.sh maestro.sh

# Or copy the script
# cp maestro/maestro.sh .

# Run initial setup
./maestro.sh init
```

## Step 2: Create Reclass Inventory Structure

### Network Base Classes

```bash
mkdir -p inventory/classes/network
```

**inventory/classes/network/base.yml:**
```yaml
classes: []

parameters:
  network:
    domain: home.local
    dns_servers:
      - 192.168.1.1
      - 8.8.8.8
    ntp_servers:
      - pool.ntp.org
    gateway: 192.168.1.1
    
  users:
    homeuser:
      name: homeuser
      groups: [sudo, docker]
      shell: /bin/bash
      ssh_authorized_keys:
        - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... homeuser@management"
  
  packages:
    common:
      - curl
      - wget
      - htop
      - vim
      - git
      - python3
      - python3-pip
      
  security:
    ssh_port: 22
    ufw_enabled: true
    fail2ban_enabled: true
```

**inventory/classes/network/home_network.yml:**
```yaml
classes:
  - network.base

parameters:
  network:
    subnets:
      management: 192.168.1.0/24
      iot: 192.168.10.0/24
      servers: 192.168.20.0/24
      
  firewall:
    allowed_ports:
      - 22      # SSH
      - 80      # HTTP  
      - 443     # HTTPS
      - 8123    # Home Assistant
      - 1883    # MQTT
      - 5000    # Various services
      
  monitoring:
    enabled: true
    node_exporter_port: 9100
    prometheus_scrape_interval: "15s"
```

### Hardware Classes

**inventory/classes/hardware/raspberry_pi.yml:**
```yaml
classes:
  - network.home_network

parameters:
  hardware:
    type: raspberry_pi
    model: pi4
    architecture: arm64
    memory: "4GB"
    
  system:
    timezone: "Europe/Berlin"
    locale: "en_US.UTF-8"
    
  ansible_connection: ssh
  ansible_user: homeuser
  ansible_python_interpreter: /usr/bin/python3
  ansible_ssh_private_key_file: ~/.ssh/id_rsa
  
  services:
    docker:
      enabled: true
      compose_version: "2.20.0"
      
  monitoring:
    node_exporter: true
    log_shipping: true
    
  maintenance:
    auto_update: true
    reboot_required_check: true
```

**inventory/classes/hardware/nas_server.yml:**
```yaml
classes:
  - network.home_network

parameters:
  hardware:
    type: nas_server
    architecture: x86_64
    
  ansible_connection: ssh
  ansible_user: root
  ansible_python_interpreter: /usr/bin/python3
    
  storage:
    zfs_enabled: true
    smart_monitoring: true
    scrub_schedule: "0 2 * * 0"  # Weekly on Sunday
    snapshot_retention: "7d,4w,12m"
    
  services:
    smb_enabled: true
    nfs_enabled: true
    ssh_enabled: true
    
  monitoring:
    zfs_monitoring: true
    disk_health_checks: true
```

### Service Classes

**inventory/classes/services/home_assistant.yml:**
```yaml
classes:
  - hardware.raspberry_pi

parameters:
  homeassistant:
    version: "latest"
    installation_type: "hassio"
    config_path: "/usr/share/hassio/homeassistant"
    backup_path: "/usr/share/hassio/backup"
    port: 8123
    ssl_enabled: true
    
  hassio_addons:
    mosquitto:
      enabled: true
      config:
        logins: []
        anonymous: false
        
    node_red:
      enabled: true
      config:
        ssl: true
        
    grafana:
      enabled: true
      
    influxdb:
      enabled: true
      
    file_editor:
      enabled: true
      
  integrations:
    mqtt:
      broker: "localhost"
      port: 1883
      
    prometheus:
      enabled: true
      
  automation:
    config_backup: true
    log_rotation: true
    health_monitoring: true
```

**inventory/classes/services/nas_services.yml:**
```yaml
classes:
  - hardware.nas_server

parameters:
  truenas:
    version: "SCALE-22.12"
    api_enabled: true
    web_port: 443
    api_port: 80
    
  zfs_pools:
    tank:
      vdevs:
        - type: mirror
          devices: ["/dev/sda", "/dev/sdb"]
        - type: mirror  
          devices: ["/dev/sdc", "/dev/sdd"]
      options:
        compression: lz4
        dedup: "off"
        atime: "off"
        
  datasets:
    media:
      pool: tank
      path: "/mnt/tank/media"
      compression: lz4
      
    backups:
      pool: tank
      path: "/mnt/tank/backups"
      compression: gzip
      
    documents:
      pool: tank
      path: "/mnt/tank/documents"
      
  smb_shares:
    media:
      path: "/mnt/tank/media"
      browseable: true
      guest_ok: false
      read_only: false
      
    backups:
      path: "/mnt/tank/backups"
      browseable: false
      guest_ok: false
      read_only: false
      
  nfs_exports:
    backups:
      path: "/mnt/tank/backups"
      clients: "192.168.1.0/24"
      options: "rw,sync,no_subtree_check"
      
  services:
    plex:
      enabled: true
      port: 32400
      media_libraries:
        - name: "Movies"
          path: "/mnt/tank/media/movies"
        - name: "TV Shows"
          path: "/mnt/tank/media/tv"
          
    nextcloud:
      enabled: false
      port: 8080
      data_path: "/mnt/tank/nextcloud"
```

## Step 3: Define Individual Nodes

### Home Assistant Node

```bash
mkdir -p inventory/nodes/homeassistant
```

**inventory/nodes/homeassistant/ha-main.yml:**
```yaml
classes:
  - services.home_assistant

parameters:
  networking:
    ip_address: 192.168.1.100
    hostname: ha-main.home.local
    interface: eth0
    
  ansible_host: 192.168.1.100
  
  homeassistant:
    device_name: "Home Assistant Main"
    location: "Server Closet"
    external_url: "https://ha-main.home.local:8123"
    
  hardware_gpio:
    enabled: true
    
  usb_devices:
    zwave:
      device: "/dev/ttyUSB0"
      description: "Z-Wave controller"
      
    zigbee:
      device: "/dev/ttyUSB1" 
      description: "Zigbee coordinator"
      
  mqtt_config:
    topics:
      - "home/+/+"
      - "homeassistant/+/+"
      - "zigbee2mqtt/+/+"
      
  backup:
    local_enabled: true
    nas_enabled: true
    nas_path: "/mnt/tank/backups/homeassistant"
    schedule: "0 3 * * *"  # Daily at 3 AM
```

### NAS Server Node

```bash
mkdir -p inventory/nodes/nas
```

**inventory/nodes/nas/truenas-main.yml:**
```yaml
classes:
  - services.nas_services

parameters:
  networking:
    ip_address: 192.168.1.200
    hostname: truenas-main.home.local
    interface: enp3s0
    
  ansible_host: 192.168.1.200
  
  storage:
    boot_device: "/dev/nvme0n1"
    data_devices:
      - "/dev/sda"  # 4TB WD Red
      - "/dev/sdb"  # 4TB WD Red  
      - "/dev/sdc"  # 4TB WD Red
      - "/dev/sdd"  # 4TB WD Red
      
  users:
    media_user:
      uid: 1001
      gid: 1001
      home: "/mnt/tank/users/media"
      groups: ["media", "users"]
      
    backup_user:
      uid: 1002
      gid: 1002
      home: "/mnt/tank/users/backup"
      groups: ["backup", "users"]
      
  scheduled_tasks:
    backup_homeassistant:
      command: "rsync -av homeuser@192.168.1.100:/usr/share/hassio/backup/ /mnt/tank/backups/homeassistant/"
      schedule: "0 4 * * *"  # Daily at 4 AM
      user: "backup_user"
      
    scrub_tank:
      command: "zpool scrub tank"
      schedule: "0 2 * * 0"  # Weekly on Sunday
      user: "root"
      
    smart_test:
      command: "/usr/sbin/smartctl -t short /dev/sd[a-d]"
      schedule: "0 1 * * 0"  # Weekly on Sunday
      user: "root"
```

## Step 4: Create Ansible Playbooks

### Main Site Playbook

```bash
mkdir -p playbooks
```

**playbooks/site.yml:**
```yaml
---
- name: Home Network Infrastructure Setup
  hosts: all
  become: yes
  gather_facts: yes
  
  vars:
    ansible_managed: "{{ ansible_managed | default('Managed by Maestro') }}"
  
  pre_tasks:
    - name: Update package cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"
      
    - name: Update package cache (RedHat)
      yum:
        update_cache: yes
      when: ansible_os_family == "RedHat"
      
  tasks:
    - name: Install common packages
      package:
        name: "{{ packages.common }}"
        state: present
      when: packages.common is defined
      
    - name: Create common users
      user:
        name: "{{ item.value.name }}"
        groups: "{{ item.value.groups | default([]) }}"
        shell: "{{ item.value.shell | default('/bin/bash') }}"
        create_home: yes
      with_dict: "{{ users | default({}) }}"
      
    - name: Set up SSH authorized keys
      authorized_key:
        user: "{{ item.value.name }}"
        key: "{{ item.value.ssh_authorized_keys | join('\n') }}"
        state: present
      with_dict: "{{ users | default({}) }}"
      when: item.value.ssh_authorized_keys is defined
      
    - name: Configure UFW firewall
      ufw:
        rule: allow
        port: "{{ item }}"
        proto: tcp
      with_items: "{{ firewall.allowed_ports | default([]) }}"
      when: security.ufw_enabled | default(false)
      
    - name: Enable UFW
      ufw:
        state: enabled
      when: security.ufw_enabled | default(false)

- name: Home Assistant Servers
  hosts: homeassistant
  become: yes
  
  tasks:
    - name: Check if Home Assistant is installed
      stat:
        path: "{{ homeassistant.config_path }}"
      register: ha_installed
      
    - name: Wait for Home Assistant to be ready
      uri:
        url: "http://{{ ansible_default_ipv4.address }}:{{ homeassistant.port }}/api/"
        method: GET
        status_code: [200, 401]  # 401 is ok, means API is up
      register: ha_api_check
      until: ha_api_check.status in [200, 401]
      retries: 30
      delay: 10
      when: ha_installed.stat.exists
      
    - name: Ensure USB devices are accessible
      file:
        path: "{{ item.value.device }}"
        state: file
        owner: "{{ ansible_user }}"
        group: dialout
        mode: '0660'
      with_dict: "{{ usb_devices | default({}) }}"
      ignore_errors: yes
      
    - name: Install MQTT broker (if enabled)
      systemd:
        name: mosquitto
        state: started
        enabled: yes
      when: hassio_addons.mosquitto.enabled | default(false)
      ignore_errors: yes
      
    - name: Set up HA backup script
      template:
        src: ha_backup.sh.j2
        dest: /usr/local/bin/ha_backup.sh
        mode: '0755'
      when: backup.local_enabled | default(false)
      
    - name: Schedule HA backups
      cron:
        name: "Home Assistant Backup"
        minute: "0"
        hour: "3"
        job: "/usr/local/bin/ha_backup.sh"
        user: "{{ ansible_user }}"
      when: backup.local_enabled | default(false)

- name: NAS Servers
  hosts: nas
  become: yes
  
  tasks:
    - name: Install ZFS utilities
      package:
        name:
          - zfsutils-linux
          - smartmontools
          - nfs-kernel-server
          - samba
          - samba-common-bin
        state: present
        
    - name: Check existing ZFS pools
      shell: zpool list | grep -v NAME | awk '{print $1}'
      register: existing_pools
      changed_when: false
      failed_when: false
      
    - name: Create ZFS pools
      shell: |
        zpool create {{ item.key }} {{ item.value.vdevs | map('regex_replace', '^.*$', item.value.vdevs) | join(' ') }}
      with_dict: "{{ zfs_pools | default({}) }}"
      when: item.key not in existing_pools.stdout_lines
      ignore_errors: yes
      
    - name: Set ZFS pool properties
      shell: |
        zfs set {{ item[1].key }}={{ item[1].value }} {{ item[0].key }}
      with_nested:
        - "{{ zfs_pools | default({}) | dict2items }}"
        - "{{ item[0].value.options | default({}) | dict2items }}"
      when: zfs_pools is defined
      
    - name: Create ZFS datasets
      zfs:
        name: "{{ item.value.pool }}/{{ item.key }}"
        state: present
        extra_zfs_properties:
          mountpoint: "{{ item.value.path }}"
          compression: "{{ item.value.compression | default('lz4') }}"
      with_dict: "{{ datasets | default({}) }}"
      
    - name: Configure Samba
      template:
        src: smb.conf.j2
        dest: /etc/samba/smb.conf
        backup: yes
      notify: restart_samba
      when: smb_shares is defined
      
    - name: Configure NFS exports
      template:
        src: exports.j2
        dest: /etc/exports
        backup: yes
      notify: restart_nfs
      when: nfs_exports is defined
      
    - name: Setup ZFS scrubbing
      cron:
        name: "ZFS scrub {{ item.key }}"
        minute: "0"
        hour: "2"
        weekday: "0"
        job: "zpool scrub {{ item.key }}"
      with_dict: "{{ zfs_pools | default({}) }}"
      
    - name: Setup SMART monitoring
      template:
        src: smartd.conf.j2
        dest: /etc/smartd.conf
        backup: yes
      notify: restart_smartd
      
  handlers:
    - name: restart_samba
      systemd:
        name: smbd
        state: restarted
        
    - name: restart_nfs
      systemd:
        name: nfs-kernel-server
        state: restarted
        
    - name: restart_smartd
      systemd:
        name: smartd
        state: restarted
```

### Health Check Playbook

**playbooks/health-check.yml:**
```yaml
---
- name: Home Network Health Check
  hosts: all
  gather_facts: yes
  
  tasks:
    - name: Check system uptime
      shell: uptime
      register: system_uptime
      
    - name: Check disk usage
      shell: df -h
      register: disk_usage
      
    - name: Check memory usage
      shell: free -h
      register: memory_usage
      
    - name: Check network connectivity to gateway
      shell: ping -c 3 {{ network.gateway | default('192.168.1.1') }}
      register: gateway_ping
      failed_when: false
      
    - name: Display system information
      debug:
        msg:
          - "Host: {{ inventory_hostname }}"
          - "Uptime: {{ system_uptime.stdout }}"
          - "Disk Usage: {{ disk_usage.stdout_lines }}"
          - "Memory: {{ memory_usage.stdout_lines }}"
          - "Gateway Connectivity: {{ 'OK' if gateway_ping.rc == 0 else 'FAILED' }}"

- name: Home Assistant Specific Checks
  hosts: homeassistant
  gather_facts: no
  
  tasks:
    - name: Check Home Assistant API
      uri:
        url: "http://{{ ansible_host }}:{{ homeassistant.port }}/api/"
        method: GET
        status_code: [200, 401]
      register: ha_api_status
      failed_when: false
      
    - name: Check USB devices
      stat:
        path: "{{ item.value.device }}"
      register: usb_device_status
      with_dict: "{{ usb_devices | default({}) }}"
      
    - name: Display HA status
      debug:
        msg:
          - "Home Assistant API: {{ 'OK' if ha_api_status.status in [200, 401] else 'FAILED' }}"
          - "USB Devices: {{ usb_device_status.results | map(attribute='stat.exists') | list }}"

- name: NAS Specific Checks
  hosts: nas
  gather_facts: no
  
  tasks:
    - name: Check ZFS pool status
      shell: zpool status
      register: zpool_status
      
    - name: Check ZFS pool health
      shell: zpool list -H -o health
      register: zpool_health
      
    - name: Check disk health with SMART
      shell: smartctl -H {{ item }} | grep "SMART overall-health"
      register: smart_health
      with_items: "{{ storage.data_devices | default([]) }}"
      failed_when: false
      
    - name: Display NAS status
      debug:
        msg:
          - "ZFS Pool Status: {{ zpool_status.stdout_lines }}"
          - "ZFS Pool Health: {{ zpool_health.stdout }}"
          - "SMART Health: {{ smart_health.results | map(attribute='stdout') | list }}"
```

## Step 5: Running Maestro Operations

### Initial Setup

```bash
# Initialize the project (clone repositories)
./maestro.sh init

# Validate configuration  
./maestro.sh config

# Test connectivity to all nodes
./maestro.sh ping

# Run setup in dry-run mode (safe)
./maestro.sh setup

# Run actual setup (remove dry_run=true from .maestro first)
./maestro.sh setup
```

### Daily Operations

```bash
# Check status of all devices
./maestro.sh status

# Run health checks
./maestro.sh ansible-playbook playbooks/health-check.yml

# Update all systems
./maestro.sh ansible-playbook playbooks/site.yml

# Run specific tasks on Home Assistant
./maestro.sh ansible homeassistant -m shell -a "systemctl status hassio-supervisor"

# Check NAS storage
./maestro.sh ansible nas -m shell -a "zpool status"

# Backup operations
./maestro.sh ansible-playbook playbooks/backup.yml
```

### Inventory Management

```bash
# List all nodes
./maestro.sh inventory --list

# Show specific node configuration
./maestro.sh inventory --host ha-main

# Validate inventory structure
./maestro.sh inventory --graph
```

### Advanced Operations

```bash
# Update repositories
./maestro.sh update

# Clean working directory
./maestro.sh clean

# Force operation (skip confirmations)
./maestro.sh -f setup

# Verbose output
./maestro.sh -v ansible-playbook playbooks/site.yml

# Debug mode
./maestro.sh -vv status
```

## Step 6: Templates and Scripts

### Backup Script Template

**templates/ha_backup.sh.j2:**
```bash
#!/bin/bash
# Home Assistant Backup Script
# Generated by Maestro

set -e

HA_CONFIG="{{ homeassistant.config_path }}"
HA_BACKUP="{{ homeassistant.backup_path }}"
NAS_BACKUP="{{ backup.nas_path | default('/tmp') }}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="ha_backup_${TIMESTAMP}"

echo "Starting Home Assistant backup..."

# Create local backup via HA API
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"name": "'${BACKUP_NAME}'", "compressed": true}' \
     "http://localhost:{{ homeassistant.port }}/api/hassio/backups/new/full"

# Wait for backup to complete
sleep 60

# Sync to NAS if enabled
{% if backup.nas_enabled | default(false) %}
echo "Syncing backup to NAS..."
rsync -av "${HA_BACKUP}/" "{{ nas_ip }}:${NAS_BACKUP}/"
{% endif %}

# Cleanup old backups (keep last {{ backup.retention | default(7) }} days)
find "${HA_BACKUP}" -name "*.tar" -mtime +{{ backup.retention | default(7) }} -delete

echo "Backup completed successfully"
```

### Samba Configuration Template

**templates/smb.conf.j2:**
```ini
# Samba Configuration
# {{ ansible_managed }}

[global]
    workgroup = WORKGROUP
    server string = {{ inventory_hostname }}
    netbios name = {{ inventory_hostname }}
    security = user
    map to guest = bad user
    dns proxy = no
    
    # Performance tuning
    socket options = TCP_NODELAY IPTOS_LOWDELAY SO_RCVBUF=131072 SO_SNDBUF=131072
    read raw = yes
    write raw = yes
    max xmit = 65535
    dead time = 15
    getwd cache = yes

{% for share_name, share_config in smb_shares.items() %}
[{{ share_name }}]
    path = {{ share_config.path }}
    browseable = {{ share_config.browseable | default('yes') }}
    guest ok = {{ share_config.guest_ok | default('no') }}
    read only = {{ share_config.read_only | default('no') }}
    create mask = 0664
    directory mask = 0775
    
{% endfor %}
```

### NFS Exports Template

**templates/exports.j2:**
```
# NFS Exports
# {{ ansible_managed }}

{% for export_name, export_config in nfs_exports.items() %}
{{ export_config.path }} {{ export_config.clients }}({{ export_config.options }})
{% endfor %}
```

## Step 7: Monitoring and Maintenance

### System Health Script

**scripts/health_check.sh:**
```bash
#!/bin/bash
# System Health Check Script

echo "=== Home Network Health Check ==="
echo "Generated: $(date)"
echo ""

# Check network connectivity
echo "Network Connectivity:"
ping -c 1 192.168.1.100 >/dev/null 2>&1 && echo "✅ Home Assistant" || echo "❌ Home Assistant"
ping -c 1 192.168.1.200 >/dev/null 2>&1 && echo "✅ NAS Server" || echo "❌ NAS Server"
ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "✅ Internet" || echo "❌ Internet"
echo ""

# Run Maestro status check
echo "Maestro Status:"
./maestro.sh status

# Run health check playbook
echo ""
echo "Detailed Health Check:"
./maestro.sh ansible-playbook playbooks/health-check.yml
```

### Scheduled Maintenance

Add to your system crontab:

```bash
# Edit crontab
crontab -e

# Add these entries:
# Daily health check at 6 AM
0 6 * * * cd /home/user/home-automation && ./scripts/health_check.sh | mail -s "Home Network Status" admin@home.local

# Weekly maintenance on Sunday at 1 AM  
0 1 * * 0 cd /home/user/home-automation && ./maestro.sh ansible-playbook playbooks/maintenance.yml

# Monthly updates on first Sunday at 3 AM
0 3 1-7 * 0 cd /home/user/home-automation && ./maestro.sh ansible-playbook playbooks/site.yml --tags updates
```

## Migration to Pyestro

When you're ready to migrate to the modern Pyestro system:

```bash
# Export current Maestro configuration
./maestro.sh export-config > maestro-export.json

# Install Pyestro
pip install pyestro

# Initialize new Pyestro project
python pyestro.py init --from-maestro .maestro

# Migrate inventory structure
python pyestro.py migrate --inventory ./inventory

# Validate new configuration
python pyestro.py config validate

# Test migration
python pyestro.py status --dry-run
```

## Troubleshooting

### Common Issues

#### Maestro Script Not Found
```bash
# Check if script is executable
ls -la maestro.sh

# Make executable if needed
chmod +x maestro.sh

# Check symlink
ls -la maestro/maestro.sh
```

#### SSH Connection Issues
```bash
# Test SSH connectivity manually
ssh homeuser@192.168.1.100

# Check SSH keys
ssh-add -l

# Test with verbose SSH
ssh -v homeuser@192.168.1.100
```

#### Ansible Errors
```bash
# Test Ansible connectivity
./maestro.sh ansible all -m ping

# Check inventory
./maestro.sh inventory --list

# Validate playbook syntax
ansible-playbook --syntax-check playbooks/site.yml
```

#### Reclass Issues
```bash
# Test reclass directly
reclass -n ha-main

# Check inventory structure
find inventory -name "*.yml" | head -10

# Validate YAML syntax
yamllint inventory/
```

## Security Considerations

### SSH Security
- Use SSH keys instead of passwords
- Disable root SSH access where possible
- Use non-standard SSH ports if desired
- Implement fail2ban for brute force protection

### Configuration Security  
- Store `.maestro` file securely (contains paths and settings)
- Use Ansible Vault for sensitive data
- Restrict file permissions on configuration files
- Keep backups of working configurations

### Network Security
- Implement proper firewall rules
- Use VLANs to segment network traffic
- Monitor network access and unusual activity
- Keep systems updated with security patches

This tutorial provides a comprehensive guide for using the original bash-based Maestro system to manage a home network infrastructure, while also showing the migration path to the modern Pyestro system.
