# Home Network Automation Tutorial

Learn how to use Pyestro to manage your home infrastructure including Raspberry Pi devices running Home Assistant and a NAS server with TrueNAS or OpenMediaVault.

## Overview

This tutorial will guide you through setting up Pyestro to manage:

- **Raspberry Pi 4** running Home Assistant OS
- **NAS Server** running TrueNAS SCALE or OpenMediaVault
- **Network Services** like Pi-hole, Nginx proxy, monitoring
- **Backup and Maintenance** automation

## Prerequisites

### Hardware Setup
- Raspberry Pi 4 (4GB+ RAM recommended) with Home Assistant OS
- NAS server (dedicated hardware or repurposed PC) with TrueNAS SCALE/OMV
- Network switch/router with SSH access capability
- SD card and USB storage for backups

### Software Requirements
- Pyestro installed on your management machine (laptop/desktop)
- SSH access enabled on all target devices
- Basic knowledge of YAML and networking

### Quick Setup Option

🚀 **For a fast start, download and run our setup script:**

```bash
curl -O https://raw.githubusercontent.com/pyestro/docs/tutorials/setup-home-network.sh
chmod +x setup-home-network.sh
./setup-home-network.sh
```

This script will create a complete project structure with templates and examples.

### Manual Setup (Detailed Below)

Continue reading for a complete step-by-step setup guide.

## Project Structure

```
home-automation/
├── pyestro.yml                 # Main configuration
├── inventory/                  # Device and service definitions
│   ├── classes/
│   │   ├── hardware/          # Hardware-specific configs
│   │   ├── services/          # Service definitions
│   │   ├── network/           # Network configurations
│   │   └── security/          # Security policies
│   └── nodes/                 # Individual device configs
│       ├── homeassistant/
│       ├── nas/
│       └── monitoring/
├── playbooks/                 # Ansible automation
│   ├── site.yml              # Main playbook
│   ├── homeassistant.yml     # HA-specific tasks
│   ├── nas-setup.yml         # NAS configuration
│   └── backup.yml            # Backup procedures
└── roles/                     # Custom automation roles
    ├── home-assistant/
    ├── nas-server/
    ├── monitoring/
    └── backup/
```

## Step 1: Initial Pyestro Setup

### Create Project Directory

```bash
mkdir ~/home-automation
cd ~/home-automation
```

### Initialize Pyestro Configuration

```bash
python pyestro.py init --template home-network
```

This creates a `pyestro.yml` with home network defaults:

```yaml
maestro:
  project_dir: /home/user/home-automation
  work_dir: ./workdir
  dry_run: true
  verbose: 2

repositories:
  home_automation_playbooks: https://github.com/home-automation/ansible-playbooks.git
  raspberry_pi_roles: https://github.com/raspberry-pi/ansible-roles.git
  nas_automation: https://github.com/nas-tools/automation.git

inventory:
  backend: reclass
  sources:
    main: ./inventory

playbooks:
  main: ./playbooks
  roles: ./roles
  galaxy_roles: ./.ansible-galaxy-roles

ansible:
  timeout: 120
  host_key_checking: false
  gathering: smart
  vault_password_file: ./vault_pass.txt

backup:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM
  retention_days: 30
  destinations:
    - type: local
      path: ./backups
    - type: nas
      path: /mnt/backups/home-automation
```

## Step 2: Define Your Home Network Inventory

### Network Infrastructure Classes

```bash
mkdir -p inventory/classes/network
```

**inventory/classes/network/home_network.yml:**
```yaml
classes:
  - network.base

parameters:
  network:
    domain: home.local
    dns_servers:
      - 192.168.1.1
      - 8.8.8.8
    ntp_servers:
      - pool.ntp.org
    subnets:
      management: 192.168.1.0/24
      iot: 192.168.10.0/24
      servers: 192.168.20.0/24
  
  security:
    ssh_port: 22
    fail2ban_enabled: true
    ufw_enabled: true
    monitoring_enabled: true
```

**inventory/classes/network/base.yml:**
```yaml
parameters:
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
```

### Hardware-Specific Classes

**inventory/classes/hardware/raspberry_pi.yml:**
```yaml
classes:
  - network.home_network

parameters:
  hardware:
    type: raspberry_pi
    model: pi4
    architecture: arm64
    
  system:
    timezone: Europe/Berlin
    locale: en_US.UTF-8
    
  monitoring:
    node_exporter: true
    log_aggregation: true
    
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
    
  storage:
    zfs_enabled: true
    smart_monitoring: true
    scrub_schedule: "0 2 * * 0"  # Weekly on Sunday
    
  services:
    smb_enabled: true
    nfs_enabled: true
    ftp_enabled: false
    
  backup:
    snapshot_enabled: true
    retention_policy: "7d,4w,12m"
```

### Service Classes

**inventory/classes/services/home_assistant.yml:**
```yaml
classes:
  - hardware.raspberry_pi

parameters:
  homeassistant:
    version: latest
    config_path: /usr/share/hassio/homeassistant
    port: 8123
    ssl_enabled: true
    
  addons:
    - name: mosquitto
      enabled: true
    - name: node-red
      enabled: true
    - name: grafana
      enabled: true
    - name: influxdb
      enabled: true
      
  integrations:
    mqtt:
      broker: localhost
      port: 1883
    zwave:
      device: /dev/ttyUSB0
    zigbee:
      device: /dev/ttyUSB1
      
  automation:
    backup_enabled: true
    config_sync: true
    log_rotation: true
```

**inventory/classes/services/nas_services.yml:**
```yaml
classes:
  - hardware.nas_server

parameters:
  truenas:
    api_enabled: true
    web_port: 443
    
  shares:
    media:
      path: /mnt/tank/media
      type: smb
      readonly: false
      guests_allowed: false
      
    backups:
      path: /mnt/tank/backups
      type: nfs
      readonly: false
      
    documents:
      path: /mnt/tank/documents
      type: smb
      readonly: false
      
  services:
    plex:
      enabled: true
      port: 32400
      media_paths:
        - /mnt/tank/media/movies
        - /mnt/tank/media/tv
        
    nextcloud:
      enabled: true
      port: 8080
      data_path: /mnt/tank/nextcloud
      
    monitoring:
      grafana_enabled: true
      prometheus_enabled: true
```

## Step 3: Define Individual Nodes

### Home Assistant Node

**inventory/nodes/homeassistant/ha-main.yml:**
```yaml
classes:
  - services.home_assistant

parameters:
  networking:
    ip_address: 192.168.1.100
    hostname: ha-main
    
  homeassistant:
    device_name: "Home Assistant Main"
    location: "Living Room"
    
  hardware_specific:
    gpio_enabled: true
    camera_enabled: true
    bluetooth_enabled: true
    
  mqtt:
    topics:
      - "home/+/+"
      - "homeassistant/+/+"
      
  backup:
    local_backup: true
    nas_backup: true
    cloud_backup: false
```

### NAS Server Node

**inventory/nodes/nas/truenas-main.yml:**
```yaml
classes:
  - services.nas_services

parameters:
  networking:
    ip_address: 192.168.1.200
    hostname: truenas-main
    
  storage:
    pools:
      tank:
        devices:
          - /dev/sda
          - /dev/sdb
          - /dev/sdc
          - /dev/sdd
        raid_level: raidz1
        
  users:
    media_user:
      uid: 1001
      groups: [media, users]
      home_directory: /mnt/tank/users/media
      
  scheduled_tasks:
    backup_homeassistant:
      command: "rsync -av homeuser@192.168.1.100:/usr/share/hassio/backup/ /mnt/tank/backups/homeassistant/"
      schedule: "0 3 * * *"
      
    system_health_check:
      command: "/scripts/health_check.sh"
      schedule: "*/15 * * * *"
```

## Step 4: Create Automation Playbooks

### Main Site Playbook

**playbooks/site.yml:**
```yaml
---
- name: Home Network Infrastructure
  hosts: all
  become: yes
  gather_facts: yes
  
  pre_tasks:
    - name: Update package cache
      package:
        update_cache: yes
      when: ansible_os_family in ['Debian', 'RedHat']
      
  roles:
    - role: common
    - role: security
    - role: monitoring

- name: Home Assistant Servers
  hosts: homeassistant
  become: yes
  
  roles:
    - role: home-assistant
    - role: mqtt-broker
    - role: backup-client

- name: NAS Servers
  hosts: nas
  become: yes
  
  roles:
    - role: nas-server
    - role: storage-manager
    - role: backup-server

- name: Network Services
  hosts: services
  become: yes
  
  roles:
    - role: dns-server
    - role: proxy-server
    - role: monitoring-server
```

### Home Assistant Specific Playbook

**playbooks/homeassistant.yml:**
```yaml
---
- name: Configure Home Assistant
  hosts: homeassistant
  become: yes
  vars:
    ha_config_repo: https://github.com/yourusername/homeassistant-config.git
    
  tasks:
    - name: Ensure Home Assistant is running
      systemd:
        name: hassio-supervisor
        state: started
        enabled: yes
        
    - name: Wait for Home Assistant API
      uri:
        url: "http://{{ ansible_default_ipv4.address }}:8123/api/"
        headers:
          Authorization: "Bearer {{ homeassistant_token }}"
      register: ha_api_check
      until: ha_api_check.status == 200
      retries: 30
      delay: 10
      
    - name: Backup current configuration
      archive:
        path: /usr/share/hassio/homeassistant
        dest: "/tmp/ha_backup_{{ ansible_date_time.epoch }}.tar.gz"
        
    - name: Sync configuration from git
      git:
        repo: "{{ ha_config_repo }}"
        dest: /tmp/ha_config_new
        force: yes
      when: ha_config_repo is defined
      
    - name: Install HACS (Home Assistant Community Store)
      shell: |
        wget -O - https://get.hacs.xyz | bash -
      args:
        creates: /usr/share/hassio/homeassistant/custom_components/hacs
        
    - name: Configure MQTT integration
      template:
        src: mqtt_config.j2
        dest: /usr/share/hassio/homeassistant/configuration.yaml
        backup: yes
      notify: restart_homeassistant
      
    - name: Setup automation backups to NAS
      cron:
        name: "Backup HA to NAS"
        minute: "0"
        hour: "2"
        job: "rsync -av /usr/share/hassio/backup/ {{ nas_backup_path }}/homeassistant/"
        
  handlers:
    - name: restart_homeassistant
      uri:
        url: "http://{{ ansible_default_ipv4.address }}:8123/api/services/homeassistant/restart"
        method: POST
        headers:
          Authorization: "Bearer {{ homeassistant_token }}"
```

### NAS Setup Playbook

**playbooks/nas-setup.yml:**
```yaml
---
- name: Configure NAS Server
  hosts: nas
  become: yes
  vars:
    zfs_pools: "{{ storage.pools }}"
    
  tasks:
    - name: Install ZFS utilities
      package:
        name:
          - zfsutils-linux
          - smartmontools
          - nfs-kernel-server
          - samba
        state: present
        
    - name: Create ZFS pools
      shell: |
        zpool create {{ item.key }} {{ item.value.raid_level }} {{ item.value.devices | join(' ') }}
      with_dict: "{{ zfs_pools }}"
      args:
        creates: "/{{ item.key }}"
        
    - name: Create ZFS datasets
      zfs:
        name: "{{ item.key }}/{{ item.value.name }}"
        state: present
        extra_zfs_properties:
          mountpoint: "{{ item.value.mountpoint }}"
          compression: lz4
          dedup: "off"
      with_dict: "{{ zfs_datasets }}"
      
    - name: Configure Samba shares
      template:
        src: smb.conf.j2
        dest: /etc/samba/smb.conf
        backup: yes
      notify: restart_samba
      
    - name: Configure NFS exports
      template:
        src: exports.j2
        dest: /etc/exports
        backup: yes
      notify: restart_nfs
      
    - name: Setup automated scrubbing
      cron:
        name: "ZFS scrub {{ item.key }}"
        weekday: "0"
        hour: "2"
        minute: "0"
        job: "zpool scrub {{ item.key }}"
      with_dict: "{{ zfs_pools }}"
      
    - name: Configure SMART monitoring
      template:
        src: smartd.conf.j2
        dest: /etc/smartd.conf
      notify: restart_smartd
      
    - name: Setup backup scripts
      template:
        src: backup_script.sh.j2
        dest: /usr/local/bin/backup_{{ item.name }}.sh
        mode: '0755'
      with_items: "{{ backup_jobs }}"
      
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

## Step 5: Security and Monitoring

### Security Role

**roles/security/tasks/main.yml:**
```yaml
---
- name: Configure UFW firewall
  ufw:
    rule: "{{ item.rule }}"
    port: "{{ item.port }}"
    proto: "{{ item.proto | default('tcp') }}"
  with_items:
    - { rule: allow, port: "{{ ssh_port }}" }
    - { rule: allow, port: "8123" }  # Home Assistant
    - { rule: allow, port: "443" }   # TrueNAS Web UI
    - { rule: allow, port: "139,445", proto: tcp }  # Samba
    - { rule: allow, port: "2049", proto: tcp }     # NFS
    
- name: Enable UFW
  ufw:
    state: enabled
    
- name: Install and configure fail2ban
  package:
    name: fail2ban
    state: present
    
- name: Configure fail2ban for SSH
  template:
    src: jail.local.j2
    dest: /etc/fail2ban/jail.local
  notify: restart_fail2ban
  
- name: Setup automatic security updates
  package:
    name: unattended-upgrades
    state: present
  when: ansible_os_family == "Debian"
```

### Monitoring Role

**roles/monitoring/tasks/main.yml:**
```yaml
---
- name: Install monitoring tools
  package:
    name:
      - htop
      - iotop
      - nethogs
      - ncdu
    state: present
    
- name: Install Node Exporter
  get_url:
    url: https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
    dest: /tmp/node_exporter.tar.gz
    
- name: Extract Node Exporter
  unarchive:
    src: /tmp/node_exporter.tar.gz
    dest: /opt/
    remote_src: yes
    
- name: Create Node Exporter systemd service
  template:
    src: node_exporter.service.j2
    dest: /etc/systemd/system/node_exporter.service
  notify: 
    - reload_systemd
    - start_node_exporter
    
- name: Setup log rotation
  logrotate:
    name: homeassistant
    path: /usr/share/hassio/homeassistant/home-assistant.log
    options:
      - daily
      - rotate 7
      - compress
      - delaycompress
      - missingok
      - notifempty
```

## Step 6: Running Your Home Automation

### Initial Setup

```bash
# Validate configuration
python pyestro.py config validate

# Check connectivity to all devices
python pyestro.py nodes ping

# Run setup in dry-run mode first
python pyestro.py setup --dry-run

# Run actual setup
python pyestro.py setup
```

### Daily Operations

```bash
# Check status of all devices
python pyestro.py status

# Update Home Assistant configuration
python pyestro.py ansible-playbook playbooks/homeassistant.yml

# Backup everything
python pyestro.py ansible-playbook playbooks/backup.yml

# Update all systems
python pyestro.py ansible-playbook playbooks/site.yml --tags updates
```

### Monitoring Commands

```bash
# Check NAS health
python pyestro.py ansible nas -m shell -a "zpool status"

# Check Home Assistant logs
python pyestro.py ansible homeassistant -m shell -a "tail -f /usr/share/hassio/homeassistant/home-assistant.log"

# Check disk usage across all devices
python pyestro.py ansible all -m shell -a "df -h"
```

## Step 7: Advanced Automation

### Automated Backups

**playbooks/backup.yml:**
```yaml
---
- name: Backup Home Assistant
  hosts: homeassistant
  tasks:
    - name: Create HA backup
      uri:
        url: "http://{{ ansible_default_ipv4.address }}:8123/api/hassio/backups/new/full"
        method: POST
        headers:
          Authorization: "Bearer {{ homeassistant_token }}"
        body_format: json
        body:
          name: "Auto backup {{ ansible_date_time.date }}"
          
    - name: Sync backups to NAS
      synchronize:
        src: /usr/share/hassio/backup/
        dest: "{{ nas_backup_path }}/homeassistant/"
        rsync_opts:
          - "--exclude=*.tmp"

- name: Backup NAS Configuration
  hosts: nas
  tasks:
    - name: Backup TrueNAS config
      shell: |
        cli -c "system config_save" > /tmp/truenas_config_{{ ansible_date_time.date }}.db
        
    - name: Create ZFS snapshots
      shell: |
        zfs snapshot {{ item }}@backup_{{ ansible_date_time.epoch }}
      with_items:
        - tank/media
        - tank/documents
        - tank/backups
```

### Health Monitoring

**scripts/health_check.sh:**
```bash
#!/bin/bash

# Health check script for home network

check_service() {
    local service=$1
    local host=$2
    local port=$3
    
    if timeout 5 bash -c "</dev/tcp/$host/$port"; then
        echo "✅ $service ($host:$port) is UP"
        return 0
    else
        echo "❌ $service ($host:$port) is DOWN"
        return 1
    fi
}

# Check critical services
check_service "Home Assistant" "192.168.1.100" "8123"
check_service "TrueNAS" "192.168.1.200" "443"
check_service "SSH HA" "192.168.1.100" "22"
check_service "SSH NAS" "192.168.1.200" "22"

# Check disk space
echo ""
echo "💾 Disk Usage:"
python pyestro.py ansible all -m shell -a "df -h | grep -E '(Filesystem|/dev/)'"

# Check ZFS health
echo ""
echo "🗄️ ZFS Status:"
python pyestro.py ansible nas -m shell -a "zpool status"

# Check Home Assistant status
echo ""
echo "🏠 Home Assistant Status:"
python pyestro.py ansible homeassistant -m shell -a "systemctl status hassio-supervisor"
```

### Scheduled Maintenance

Add to crontab on your management machine:

```bash
# Daily health check at 6 AM
0 6 * * * cd /home/user/home-automation && /usr/local/bin/health_check.sh | mail -s "Home Network Status" admin@home.local

# Weekly full backup on Sunday at 1 AM  
0 1 * * 0 cd /home/user/home-automation && python pyestro.py ansible-playbook playbooks/backup.yml

# Monthly system updates on first Sunday at 3 AM
0 3 1-7 * 0 cd /home/user/home-automation && python pyestro.py ansible-playbook playbooks/site.yml --tags updates
```

## Troubleshooting

### Common Issues

#### Home Assistant Connection Problems
```bash
# Check if HA is running
python pyestro.py ansible homeassistant -m shell -a "systemctl status hassio-supervisor"

# Check network connectivity
python pyestro.py ansible homeassistant -m ping

# Check HA logs
python pyestro.py ansible homeassistant -m shell -a "journalctl -u hassio-supervisor -f"
```

#### NAS Storage Issues
```bash
# Check ZFS pool status
python pyestro.py ansible nas -m shell -a "zpool status"

# Check disk health
python pyestro.py ansible nas -m shell -a "smartctl -a /dev/sda"

# Check Samba shares
python pyestro.py ansible nas -m shell -a "smbclient -L localhost -N"
```

#### Network Connectivity
```bash
# Test all connections
python pyestro.py nodes ping

# Check firewall status
python pyestro.py ansible all -m shell -a "ufw status"

# Network diagnostics
python pyestro.py ansible all -m shell -a "ss -tlnp"
```

## Next Steps

### Expand Your Setup
- Add more Raspberry Pi devices for different rooms
- Implement IoT device management
- Set up external monitoring with Grafana
- Configure automated alerts via Home Assistant

### Security Enhancements
- Implement VPN access for remote management
- Set up certificate management with Let's Encrypt
- Configure network segmentation
- Add intrusion detection

### Advanced Features
- Implement GitOps workflows for configuration
- Set up continuous integration for playbook testing
- Add infrastructure as code for network devices
- Implement disaster recovery procedures

## Additional Resources

### Template Files

- **[Configuration Template](home-network-template.yml)** - Complete pyestro.yml template for home networks
- **[Setup Script](setup-home-network.sh)** - Automated project bootstrap script

### Example Configurations

For more examples and advanced configurations, check out:

- **Smart Home Integration** - IoT device management examples
- **Advanced Monitoring** - Prometheus + Grafana setup
- **Security Hardening** - Best practices for home network security
- **Backup Strategies** - Multi-tier backup configurations

### Community Examples

Visit the Pyestro community repository for more real-world examples:
- Home lab setups
- Small office configurations  
- IoT device automation
- Monitoring and alerting configurations
