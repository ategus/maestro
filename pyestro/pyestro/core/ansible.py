"""
Ansible integration for Pyestro.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..core.config import MaestroConfig, log_info, log_warning
from ..core.validation import InputValidator


class AnsibleManager:
    """Manages Ansible operations."""
    
    def __init__(self, config: MaestroConfig):
        self.config = config
        self.ansible_path = self._find_ansible()
        self.ansible_playbook_path = self._find_ansible_playbook()
    
    def _find_ansible(self) -> Optional[str]:
        """Find ansible executable."""
        ansible_path = shutil.which("ansible")
        if not ansible_path:
            log_warning("ansible executable not found")
        return ansible_path
    
    def _find_ansible_playbook(self) -> Optional[str]:
        """Find ansible-playbook executable."""
        ansible_playbook_path = shutil.which("ansible-playbook")
        if not ansible_playbook_path:
            log_warning("ansible-playbook executable not found")
        return ansible_playbook_path
    
    def execute_module(
        self,
        module_name: str,
        module_args: List[str],
        hosts: str = "all",
        extra_vars: Optional[Dict[str, str]] = None
    ) -> bool:
        """Execute an Ansible module."""
        if not self.ansible_path:
            log_warning("Cannot execute ansible module: ansible not available")
            return False
        
        # Validate inputs
        try:
            module_name = InputValidator.validate_ansible_module_name(module_name)
            module_args = InputValidator.sanitize_command_args(module_args)
        except Exception as e:
            log_warning(f"Invalid module or arguments: {e}")
            return False
        
        # Build command
        cmd = [self.ansible_path, hosts, "-m", module_name]
        
        # Add module arguments
        if module_args:
            cmd.extend(["-a", " ".join(module_args)])
        
        # Add extra variables
        if extra_vars:
            extra_vars_str = " ".join([f"{k}={v}" for k, v in extra_vars.items()])
            cmd.extend(["-e", extra_vars_str])
        
        # Add inventory
        inventory_path = self.config.merged_inventory_dir / "hosts"
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        
        # Add verbosity
        if self.config.verbose > 1:
            cmd.append("-" + "v" * min(self.config.verbose - 1, 4))
        
        log_info(f"Executing Ansible module: {module_name}")
        
        if self.config.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return True
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                text=True
            )
            log_info(f"Ansible module {module_name} executed successfully")
            return True
        except subprocess.CalledProcessError as e:
            log_warning(f"Ansible module {module_name} failed: {e}")
            return False
    
    def run_playbook(
        self,
        playbook_path: Path,
        hosts: Optional[str] = None,
        extra_vars: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        skip_tags: Optional[List[str]] = None
    ) -> bool:
        """Run an Ansible playbook."""
        if not self.ansible_playbook_path:
            log_warning("Cannot run playbook: ansible-playbook not available")
            return False
        
        if not playbook_path.exists():
            log_warning(f"Playbook not found: {playbook_path}")
            return False
        
        # Build command
        cmd = [self.ansible_playbook_path, str(playbook_path)]
        
        # Add inventory
        inventory_path = self.config.merged_inventory_dir / "hosts"
        if inventory_path.exists():
            cmd.extend(["-i", str(inventory_path)])
        
        # Limit to specific hosts
        if hosts:
            try:
                hosts = InputValidator.sanitize_shell_input(hosts)
                cmd.extend(["-l", hosts])
            except Exception as e:
                log_warning(f"Invalid hosts pattern: {e}")
                return False
        
        # Add extra variables
        if extra_vars:
            extra_vars_str = " ".join([f"{k}={v}" for k, v in extra_vars.items()])
            cmd.extend(["-e", extra_vars_str])
        
        # Add tags
        if tags:
            cmd.extend(["-t", ",".join(tags)])
        
        if skip_tags:
            cmd.extend(["--skip-tags", ",".join(skip_tags)])
        
        # Add verbosity
        if self.config.verbose > 1:
            cmd.append("-" + "v" * min(self.config.verbose - 1, 4))
        
        # Add check mode for dry run
        if self.config.dry_run:
            cmd.append("--check")
        
        log_info(f"Running Ansible playbook: {playbook_path}")
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                text=True
            )
            log_info(f"Playbook {playbook_path} executed successfully")
            return True
        except subprocess.CalledProcessError as e:
            log_warning(f"Playbook {playbook_path} failed: {e}")
            return False
    
    def list_playbooks(self) -> List[Path]:
        """List available playbooks."""
        playbooks = []
        
        for playbook_dir_path in self.config.playbook_dirs.values():
            if playbook_dir_path == "none":
                continue
            
            playbook_dir = Path(playbook_dir_path)
            if playbook_dir.exists():
                # Find .yml and .yaml files
                for playbook_file in playbook_dir.rglob("*.yml"):
                    playbooks.append(playbook_file)
                for playbook_file in playbook_dir.rglob("*.yaml"):
                    playbooks.append(playbook_file)
        
        return sorted(playbooks)
    
    def ping_hosts(self, hosts: str = "all") -> bool:
        """Ping hosts to check connectivity."""
        return self.execute_module("ping", [], hosts)
    
    def gather_facts(self, hosts: str = "all") -> bool:
        """Gather facts from hosts."""
        return self.execute_module("setup", [], hosts)
    
    def create_ansible_cfg(self, output_path: Optional[Path] = None) -> Path:
        """Create ansible.cfg file with appropriate settings."""
        if not output_path:
            output_path = self.config.maestro_dir / "ansible.cfg"
        
        config_content = f"""[defaults]
inventory = {self.config.merged_inventory_dir / "hosts"}
host_key_checking = False
timeout = {self.config.ansible.timeout}
ansible_managed = {self.config.ansible.managed_banner}
roles_path = {self.config.maestro_dir / self.config.ansible.galaxy_roles_dir}

[ssh_connection]
scp_if_ssh = {'True' if self.config.ansible.scp_if_ssh else 'False'}
"""
        
        log_info(f"Creating ansible.cfg at {output_path}")
        
        if self.config.dry_run:
            log_info(f"DRY RUN: Would create ansible.cfg with content:\\n{config_content}")
            return output_path
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            log_info(f"Created ansible.cfg at {output_path}")
            return output_path
        except Exception as e:
            log_warning(f"Failed to create ansible.cfg: {e}")
            return output_path
    
    def validate_playbook(self, playbook_path: Path) -> bool:
        """Validate an Ansible playbook syntax."""
        if not self.ansible_playbook_path:
            log_warning("Cannot validate playbook: ansible-playbook not available")
            return False
        
        cmd = [
            self.ansible_playbook_path,
            str(playbook_path),
            "--syntax-check"
        ]
        
        log_info(f"Validating playbook syntax: {playbook_path}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            log_info(f"Playbook {playbook_path} syntax is valid")
            return True
        except subprocess.CalledProcessError as e:
            log_warning(f"Playbook {playbook_path} syntax check failed: {e.stderr}")
            return False
