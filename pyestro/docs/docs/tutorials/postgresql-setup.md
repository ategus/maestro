# PostgreSQL Database Setup with Backup Solution

This tutorial will guide you through setting up a robust PostgreSQL database infrastructure with automated backups using Pyestro.

## Overview

This setup provides:
- 🗄️ **Primary PostgreSQL Server** - High-performance database server
- 🔄 **Automated Backups** - Regular backups to secondary server
- 📊 **Monitoring** - Database performance and health monitoring
- 🔒 **Security** - SSL/TLS encryption and access controls
- 🚀 **High Availability** - Replication and failover capabilities

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│  Primary DB     │    │  Backup Server  │
│  PostgreSQL     │───▶│  Backup Storage │
│  192.168.1.120  │    │  192.168.1.121  │
│                 │    │                 │
│ • Production DB │    │ • Backup Files  │
│ • Read/Write    │    │ • Monitoring    │
│ • Replication   │    │ • Log Archive   │
└─────────────────┘    └─────────────────┘
```

## Prerequisites

- Two servers (physical or virtual)
- Ubuntu 20.04+ or CentOS 8+
- SSH access to both servers
- Pyestro installed and configured

## Quick Start

### 1. Create PostgreSQL Project

```bash
# Create project using the postgres template
python pyestro.py create postgres my-database \
  --var=primary_db_ip=192.168.1.120 \
  --var=backup_server_ip=192.168.1.121 \
  --var=db_name=myapp \
  --var=db_user=myapp_user \
  --var=enable_replication=y \
  --var=backup_retention_days=30
```

### 2. Navigate and Setup

```bash
cd my-database
python pyestro.py config validate
python pyestro.py setup
```

### 3. Deploy Infrastructure

```bash
# Deploy primary database server
python pyestro.py ansible playbook site.yml --limit primary-db

# Deploy backup server
python pyestro.py ansible playbook site.yml --limit backup-server

# Verify deployment
python pyestro.py status
```

## Detailed Configuration

### Primary Database Server

The primary server hosts the main PostgreSQL instance with:

- **PostgreSQL 14+** with optimized configuration
- **SSL/TLS encryption** for secure connections
- **Streaming replication** for high availability
- **Connection pooling** with PgBouncer
- **Performance monitoring** with pg_stat_statements

### Backup Server Configuration

The backup server provides comprehensive backup solutions:

- **Physical Backups** using pg_basebackup
- **Logical Backups** using pg_dump
- **WAL Archiving** for point-in-time recovery
- **Automated Cleanup** based on retention policies
- **Backup Verification** and integrity checks

### Network Security

- **Firewall Rules** restricting database access
- **SSL Certificates** for encrypted connections
- **User Authentication** with password policies
- **Connection Limits** to prevent resource exhaustion

## Configuration Files

### Primary Database (`inventory/nodes/primary-db.yml`)

```yaml
classes:
  - hardware.server
  - services.postgresql.primary
  - network.database
  - security.database
  - monitoring.postgresql

parameters:
  hostname: primary-db
  ip_address: 192.168.1.120
  
  postgresql:
    version: 14
    port: 5432
    max_connections: 200
    shared_buffers: "256MB"
    effective_cache_size: "1GB"
    
    # SSL Configuration
    ssl: true
    ssl_cert_file: "/etc/ssl/certs/postgresql.crt"
    ssl_key_file: "/etc/ssl/private/postgresql.key"
    
    # Replication
    replication:
      enabled: true
      user: "replicator"
      slots:
        - name: "backup_slot"
          
    # Databases
    databases:
      - name: "myapp"
        owner: "myapp_user"
        encoding: "UTF8"
        
    # Users
    users:
      - name: "myapp_user"
        password: "{{ vault_myapp_password }}"
        privileges: "ALL"
        database: "myapp"
```

### Backup Server (`inventory/nodes/backup-server.yml`)

```yaml
classes:
  - hardware.server
  - services.postgresql.backup
  - network.backup
  - security.backup
  - monitoring.backup

parameters:
  hostname: backup-server
  ip_address: 192.168.1.121
  
  postgresql_backup:
    primary_host: "192.168.1.120"
    primary_port: 5432
    replication_user: "replicator"
    
    # Backup Configuration
    backup_dir: "/var/lib/postgresql/backups"
    wal_archive_dir: "/var/lib/postgresql/wal_archive"
    
    # Backup Schedule
    schedules:
      full_backup:
        cron: "0 2 * * 0"  # Weekly at 2 AM Sunday
        retention: 4        # Keep 4 weeks
        
      incremental_backup:
        cron: "0 2 * * 1-6" # Daily at 2 AM Mon-Sat
        retention: 7        # Keep 7 days
        
      logical_backup:
        cron: "0 4 * * *"   # Daily at 4 AM
        retention: 30       # Keep 30 days
    
    # Monitoring
    monitoring:
      enabled: true
      alerts:
        backup_failure: true
        disk_space_low: true
        replication_lag: true
```

## Ansible Playbooks

### Main Deployment (`playbooks/site.yml`)

```yaml
---
- name: Deploy PostgreSQL Infrastructure
  hosts: all
  become: yes
  gather_facts: yes
  
  pre_tasks:
    - name: Update system packages
      package:
        name: "*"
        state: latest
      when: ansible_os_family in ['Debian', 'RedHat']

- name: Configure Primary Database Server
  hosts: primary_db
  become: yes
  roles:
    - postgresql_primary
    - monitoring
    - security

- name: Configure Backup Server
  hosts: backup_server
  become: yes
  roles:
    - postgresql_backup
    - monitoring
    - security

- name: Setup Replication
  hosts: primary_db:backup_server
  become: yes
  tasks:
    - name: Configure streaming replication
      include_role:
        name: postgresql_replication
```

### PostgreSQL Primary Role (`playbooks/roles/postgresql_primary/tasks/main.yml`)

```yaml
---
- name: Install PostgreSQL packages
  package:
    name:
      - postgresql-{{ postgresql.version }}
      - postgresql-contrib-{{ postgresql.version }}
      - postgresql-client-{{ postgresql.version }}
      - python3-psycopg2
    state: present

- name: Initialize PostgreSQL database
  command: /usr/lib/postgresql/{{ postgresql.version }}/bin/initdb -D /var/lib/postgresql/{{ postgresql.version }}/main
  become_user: postgres
  args:
    creates: /var/lib/postgresql/{{ postgresql.version }}/main/PG_VERSION

- name: Configure PostgreSQL
  template:
    src: postgresql.conf.j2
    dest: /etc/postgresql/{{ postgresql.version }}/main/postgresql.conf
    owner: postgres
    group: postgres
    mode: '0644'
  notify: restart postgresql

- name: Configure pg_hba.conf
  template:
    src: pg_hba.conf.j2
    dest: /etc/postgresql/{{ postgresql.version }}/main/pg_hba.conf
    owner: postgres
    group: postgres
    mode: '0644'
  notify: restart postgresql

- name: Start and enable PostgreSQL
  systemd:
    name: postgresql
    state: started
    enabled: yes

- name: Create databases
  postgresql_db:
    name: "{{ item.name }}"
    owner: "{{ item.owner }}"
    encoding: "{{ item.encoding | default('UTF8') }}"
    state: present
  loop: "{{ postgresql.databases }}"
  become_user: postgres

- name: Create users
  postgresql_user:
    name: "{{ item.name }}"
    password: "{{ item.password }}"
    role_attr_flags: "{{ item.role_attr_flags | default('') }}"
    db: "{{ item.database | default('postgres') }}"
    priv: "{{ item.privileges | default('') }}"
    state: present
  loop: "{{ postgresql.users }}"
  become_user: postgres
```

## Backup Scripts

### Automated Backup Script (`scripts/backup_postgresql.sh`)

```bash
#!/bin/bash
# PostgreSQL Backup Script
# Generated by Pyestro postgres template

set -euo pipefail

# Configuration
PRIMARY_HOST="{{ primary_db_ip }}"
PRIMARY_PORT="5432"
BACKUP_DIR="/var/lib/postgresql/backups"
WAL_ARCHIVE_DIR="/var/lib/postgresql/wal_archive"
RETENTION_DAYS="{{ backup_retention_days }}"
DATE=$(date +%Y%m%d_%H%M%S)

# Logging
LOG_FILE="/var/log/postgresql_backup.log"
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

echo "Starting PostgreSQL backup: $DATE"

# Create backup directories
mkdir -p "$BACKUP_DIR"/{full,incremental,logical}
mkdir -p "$WAL_ARCHIVE_DIR"

# Function: Full Backup
perform_full_backup() {
    echo "Performing full backup..."
    
    pg_basebackup \
        -h "$PRIMARY_HOST" \
        -p "$PRIMARY_PORT" \
        -U replicator \
        -D "$BACKUP_DIR/full/backup_$DATE" \
        -Ft \
        -z \
        -P \
        -W
    
    if [ $? -eq 0 ]; then
        echo "Full backup completed successfully"
        
        # Create backup info file
        cat > "$BACKUP_DIR/full/backup_$DATE.info" << EOF
Backup Type: Full
Date: $DATE
Primary Host: $PRIMARY_HOST
Backup Size: $(du -sh "$BACKUP_DIR/full/backup_$DATE" | cut -f1)
EOF
    else
        echo "Full backup failed!" >&2
        exit 1
    fi
}

# Function: Logical Backup
perform_logical_backup() {
    echo "Performing logical backup..."
    
    # Get list of databases
    DATABASES=$(psql -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -U postgres -t -c "SELECT datname FROM pg_database WHERE NOT datistemplate AND datname != 'postgres';")
    
    for db in $DATABASES; do
        echo "Backing up database: $db"
        
        pg_dump \
            -h "$PRIMARY_HOST" \
            -p "$PRIMARY_PORT" \
            -U postgres \
            -Fc \
            -f "$BACKUP_DIR/logical/${db}_$DATE.dump" \
            "$db"
        
        if [ $? -eq 0 ]; then
            echo "Logical backup of $db completed"
        else
            echo "Logical backup of $db failed!" >&2
        fi
    done
}

# Function: Cleanup Old Backups
cleanup_old_backups() {
    echo "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find "$BACKUP_DIR/full" -name "backup_*" -mtime +$RETENTION_DAYS -exec rm -rf {} \;
    find "$BACKUP_DIR/logical" -name "*.dump" -mtime +$RETENTION_DAYS -delete
    find "$WAL_ARCHIVE_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
    
    echo "Cleanup completed"
}

# Function: Verify Backup
verify_backup() {
    echo "Verifying backup integrity..."
    
    # Check if backup files exist and are not empty
    LATEST_FULL=$(find "$BACKUP_DIR/full" -name "backup_*" -type d | sort | tail -1)
    
    if [ -n "$LATEST_FULL" ] && [ -d "$LATEST_FULL" ]; then
        echo "Latest full backup found: $LATEST_FULL"
        
        # Basic verification - check if base.tar.gz exists and is not empty
        if [ -s "$LATEST_FULL/base.tar.gz" ]; then
            echo "Backup verification passed"
        else
            echo "Backup verification failed - base.tar.gz missing or empty" >&2
            exit 1
        fi
    else
        echo "No valid backup found for verification" >&2
        exit 1
    fi
}

# Main execution
case "${1:-full}" in
    "full")
        perform_full_backup
        verify_backup
        cleanup_old_backups
        ;;
    "logical")
        perform_logical_backup
        cleanup_old_backups
        ;;
    "verify")
        verify_backup
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    *)
        echo "Usage: $0 {full|logical|verify|cleanup}"
        exit 1
        ;;
esac

echo "Backup operation completed: $(date)"
```

## Monitoring and Alerting

### PostgreSQL Monitoring (`playbooks/roles/monitoring/tasks/postgresql.yml`)

```yaml
---
- name: Install monitoring tools
  package:
    name:
      - prometheus-node-exporter
      - prometheus-postgres-exporter
    state: present

- name: Configure PostgreSQL exporter
  template:
    src: postgres_exporter.env.j2
    dest: /etc/default/prometheus-postgres-exporter
    mode: '0600'
  notify: restart postgres_exporter

- name: Create monitoring user
  postgresql_user:
    name: monitoring
    password: "{{ vault_monitoring_password }}"
    role_attr_flags: LOGIN
    db: postgres
    priv: "pg_stat_database:SELECT,pg_stat_user_tables:SELECT"
    state: present
  become_user: postgres

- name: Start monitoring services
  systemd:
    name: "{{ item }}"
    state: started
    enabled: yes
  loop:
    - prometheus-node-exporter
    - prometheus-postgres-exporter
```

## Security Configuration

### Database Security (`playbooks/roles/security/tasks/database.yml`)

```yaml
---
- name: Configure firewall for PostgreSQL
  ufw:
    rule: allow
    port: "{{ postgresql.port }}"
    src: "{{ item }}"
  loop:
    - "{{ backup_server_ip }}"
    - "192.168.1.0/24"  # Application network

- name: Generate SSL certificates
  command: >
    openssl req -new -x509 -days 365 -nodes
    -text -out /etc/ssl/certs/postgresql.crt
    -keyout /etc/ssl/private/postgresql.key
    -subj "/CN={{ ansible_fqdn }}"
  args:
    creates: /etc/ssl/certs/postgresql.crt

- name: Set SSL certificate permissions
  file:
    path: "{{ item.path }}"
    owner: postgres
    group: postgres
    mode: "{{ item.mode }}"
  loop:
    - { path: "/etc/ssl/certs/postgresql.crt", mode: "0644" }
    - { path: "/etc/ssl/private/postgresql.key", mode: "0600" }

- name: Configure log rotation
  template:
    src: postgresql.logrotate.j2
    dest: /etc/logrotate.d/postgresql
    mode: '0644'
```

## Testing and Validation

### Connection Testing

```bash
# Test primary database connection
psql -h 192.168.1.120 -U myapp_user -d myapp -c "SELECT version();"

# Test replication status
psql -h 192.168.1.120 -U postgres -c "SELECT * FROM pg_stat_replication;"

# Test backup connectivity
pg_isready -h 192.168.1.120 -p 5432
```

### Backup Validation

```bash
# Run backup verification
./scripts/backup_postgresql.sh verify

# Test backup restoration (on test server)
./scripts/restore_postgresql.sh /var/lib/postgresql/backups/full/backup_20240101_020000
```

## Maintenance and Operations

### Regular Tasks

1. **Daily**: Monitor backup completion and replication lag
2. **Weekly**: Review database performance metrics
3. **Monthly**: Test backup restoration procedures
4. **Quarterly**: Update PostgreSQL and security patches

### Common Operations

```bash
# Manual backup
./scripts/backup_postgresql.sh full

# Check replication status
python pyestro.py ansible shell "SELECT * FROM pg_stat_replication;" --limit primary-db

# Monitor backup server disk usage
python pyestro.py ansible shell "df -h /var/lib/postgresql/backups" --limit backup-server

# Restart services
python pyestro.py ansible service "name=postgresql state=restarted" --limit primary-db
```

## Troubleshooting

### Common Issues

**Replication Not Working**
```bash
# Check replication user permissions
psql -U postgres -c "SELECT * FROM pg_user WHERE usename='replicator';"

# Verify pg_hba.conf configuration
cat /etc/postgresql/14/main/pg_hba.conf | grep replication
```

**Backup Failures**
```bash
# Check backup logs
tail -f /var/log/postgresql_backup.log

# Verify disk space
df -h /var/lib/postgresql/backups

# Test manual backup
pg_basebackup -h 192.168.1.120 -U replicator -D /tmp/test_backup -Ft
```

**Connection Issues**
```bash
# Check PostgreSQL status
systemctl status postgresql

# Verify firewall rules
ufw status

# Test network connectivity
telnet 192.168.1.120 5432
```

## Performance Tuning

### PostgreSQL Configuration

```sql
-- Recommended settings for production
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### Monitoring Queries

```sql
-- Check database size
SELECT datname, pg_size_pretty(pg_database_size(datname)) as size 
FROM pg_database;

-- Monitor active connections
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';

-- Check replication lag
SELECT client_addr, state, 
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)) as lag
FROM pg_stat_replication;
```

## Advanced Configuration

### High Availability Setup

For production environments, consider:
- **Failover Automation** using Patroni or repmgr
- **Load Balancing** with HAProxy or PgBouncer
- **Multi-Region Replication** for disaster recovery

### Backup Strategies

- **Point-in-Time Recovery**: Configure WAL archiving
- **Cross-Region Backups**: Replicate backups to remote storage
- **Encrypted Backups**: Use pg_dump with encryption

## Next Steps

1. **[Monitor Performance](../reference/monitoring.md)** - Set up comprehensive monitoring
2. **[Security Hardening](../reference/security.md)** - Additional security measures
3. **[High Availability](../tutorials/ha-setup.md)** - Implement HA solutions
4. **[Disaster Recovery](../reference/disaster-recovery.md)** - Plan for disaster scenarios

For more help, see the [PostgreSQL Documentation](https://postgresql.org/docs/) and [Troubleshooting Guide](../troubleshooting.md).