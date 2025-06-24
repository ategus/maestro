"""
Ansible integration for Pyestro.
"""

import subprocess
import shutil
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from ..core.config import MaestroConfig, AnsibleConfig, log_info, log_warning
from ..core.validation import InputValidator, ValidationError


class AnsibleManager:
    """Manages Ansible operations and playbook execution."""
    
    def __init__(self, config: MaestroConfig):
        self.config = config
        self.ansible_path = self._find_ansible()
        self.ansible_playbook_path = self._find_ansible_playbook()
        self.ansible_galaxy_path = self._find_ansible_galaxy()
    
    def _find_ansible(self) -> Optional[str]:
        """Find ansible executable."""
        ansible_path = shutil.which("ansible")
        if not ansible_path:
            log_warning("ansible executable not found in PATH")
        return ansible_path
    
    def _find_ansible_playbook(self) -> Optional[str]:
        """Find ansible-playbook executable."""
        playbook_path = shutil.which("ansible-playbook")
        if not playbook_path:
            log_warning("ansible-playbook executable not found in PATH")
        return playbook_path
    
    def _find_ansible_galaxy(self) -> Optional[str]:
        """Find ansible-galaxy executable."""
        galaxy_path = shutil.which("ansible-galaxy")
        if not galaxy_path:
            log_warning("ansible-galaxy executable not found in PATH")
        return galaxy_path
    
    def _setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for Ansible."""
        env = os.environ.copy()
        
        # Set inventory path
        inventory_path = self.config.merged_inventory_dir / "hosts"
        env["ANSIBLE_INVENTORY"] = str(inventory_path)
        
        # Set config file if specified
        if self.config.ansible.config_file:
            config_path = Path(self.config.ansible.config_file)
            if config_path.exists():
                env["ANSIBLE_CONFIG"] = str(config_path)
        
        # Set other Ansible variables
        env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
        env["ANSIBLE_TIMEOUT"] = str(self.config.ansible.timeout)
        
        return env
    
    def execute_module(
        self,
        module_name: str,
        module_args: Optional[str] = None,
        hosts: str = "all",
        extra_vars: Optional[Dict[str, Any]] = None,
        become: bool = False,
        check_mode: bool = False
    ) -> bool:
        """Execute an Ansible module."""
        if not self.ansible_path:
            log_warning("ansible not available")
            return False
        
        try:
            module_name = InputValidator.validate_ansible_module_name(module_name)
        except ValidationError as e:
            log_warning(f"Invalid module name: {e}")
            return False
        
        cmd = [self.ansible_path, hosts, "-m", module_name]
        
        if module_args:
            cmd.extend(["-a", module_args])
        
        if become:
            cmd.append("--become")
        
        if check_mode or self.config.dry_run:
            cmd.append("--check")
        
        if extra_vars:
            extra_vars_str = " ".join([f"{k}={v}" for k, v in extra_vars.items()])
            cmd.extend(["-e", extra_vars_str])
        
        if self.config.verbose > 0:
            cmd.append("-" + "v" * min(self.config.verbose, 4))
        
        log_info(f"Executing Ansible module: {module_name}")
        
        if self.config.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return True
        
        try:
            env = self._setup_environment()
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                log_info(f"Module {module_name} executed successfully")
                if self.config.verbose > 0:
                    print(result.stdout)
                return True
            else:
                log_warning(f"Module {module_name} failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            log_warning(f"Failed to execute module {module_name}: {e}")
            return False
    
    def execute_playbook(
        self,
        playbook_path: Path,
        hosts: Optional[str] = None,
        extra_vars: Optional[Dict[str, Any]] = None,
        become: bool = False,
        check_mode: bool = False,
        tags: Optional[List[str]] = None,
        skip_tags: Optional[List[str]] = None
    ) -> bool:
        """Execute an Ansible playbook."""
        if not self.ansible_playbook_path:
            log_warning("ansible-playbook not available")
            return False
        
        if not playbook_path.exists():
            log_warning(f"Playbook not found: {playbook_path}")
            return False
        
        cmd = [self.ansible_playbook_path, str(playbook_path)]
        
        if hosts:
            cmd.extend(["-l", hosts])
        
        if become:
            cmd.append("--become")
        
        if check_mode or self.config.dry_run:
            cmd.append("--check")
        
        if extra_vars:
            # Build extra vars string
            extra_vars_list = []
            for k, v in extra_vars.items():
                extra_vars_list.append(f"{k}={v}")
            # Add workdir and other standard vars
            extra_vars_list.append(f"workdir={self.config.work_dir}")
            cmd.extend(["-e", " ".join(extra_vars_list)])
        
        if tags:
            cmd.extend(["--tags", ",".join(tags)])
        
        if skip_tags:
            cmd.extend(["--skip-tags", ",".join(skip_tags)])
        
        if self.config.verbose > 0:
            cmd.append("-" + "v" * min(self.config.verbose, 4))
        
        log_info(f"Executing playbook: {playbook_path}")
        
        if self.config.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return True
        
        try:
            env = self._setup_environment()
            result = subprocess.run(
                cmd,
                env=env
            )
            
            if result.returncode == 0:
                log_info(f"Playbook {playbook_path} executed successfully")
                return True
            else:
                log_warning(f"Playbook {playbook_path} failed with return code {result.returncode}")
                return False
                
        except Exception as e:
            log_warning(f"Failed to execute playbook {playbook_path}: {e}")
            return False
    
    def install_galaxy_roles(self, requirements_file: Optional[Path] = None) -> bool:
        """Install Ansible Galaxy roles."""
        if not self.ansible_galaxy_path:
            log_warning("ansible-galaxy not available")
            return False
        
        # Find requirements file
        if not requirements_file:
            for playbook_dir in self.config.playbook_dirs.values():
                if playbook_dir and playbook_dir != "none":
                    req_path = Path(playbook_dir) / "galaxy" / "roles.yml"
                    if req_path.exists():
                        requirements_file = req_path
                        break
        
        if not requirements_file or not requirements_file.exists():
            log_info("No galaxy requirements file found, skipping role installation")
            return True
        
        roles_dir = self.config.maestro_dir / self.config.ansible.galaxy_roles_dir
        roles_dir.mkdir(exist_ok=True)
        
        cmd = [
            self.ansible_galaxy_path,
            "install",
            "-r", str(requirements_file),
            "-p", str(roles_dir),
            "--force"
        ]
        
        log_info(f"Installing Galaxy roles from {requirements_file}")
        
        if self.config.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return True
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            log_info("Galaxy roles installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            log_warning(f"Failed to install Galaxy roles: {e.stderr}")
            return False
    
    def test_connectivity(self, hosts: str = "all") -> Dict[str, bool]:
        """Test connectivity to hosts using Ansible ping module."""
        if not self.ansible_path:
            log_warning("ansible not available")
            return {}
        
        cmd = [
            self.ansible_path,
            hosts,
            "-m", "ping",
            "--one-line"
        ]
        
        if self.config.verbose > 0:
            cmd.append("-v")
        
        log_info(f"Testing connectivity to: {hosts}")
        
        if self.config.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return {"example_host": True}
        
        try:
            env = self._setup_environment()
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            # Parse output to determine which hosts are reachable
            connectivity = {}
            for line in result.stdout.splitlines():
                if " | SUCCESS" in line:
                    host = line.split(" | ")[0].strip()
                    connectivity[host] = True
                elif " | UNREACHABLE" in line or " | FAILED" in line:
                    host = line.split(" | ")[0].strip()
                    connectivity[host] = False
            
            return connectivity
            
        except Exception as e:
            log_warning(f"Failed to test connectivity: {e}")
            return {}
    
    def list_hosts(self, pattern: str = "all") -> List[str]:
        """List hosts matching a pattern."""
        if not self.ansible_path:
            log_warning("ansible not available")
            return []
        
        cmd = [
            self.ansible_path,
            pattern,
            "--list-hosts"
        ]
        
        try:
            env = self._setup_environment()
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            hosts = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith("hosts ("):
                    hosts.append(line)
            
            return hosts
            
        except subprocess.CalledProcessError as e:
            log_warning(f"Failed to list hosts: {e.stderr}")
            return []
    
    def create_ansible_cfg(self) -> bool:
        """Create a basic ansible.cfg file."""
        config_path = self.config.maestro_dir / "ansible.cfg"
        
        if config_path.exists() and not self.config.force:
            log_info(f"ansible.cfg already exists: {config_path}")
            return True
        
        config_content = f"""[defaults]
inventory = {self.config.merged_inventory_dir}/hosts
host_key_checking = False
timeout = {self.config.ansible.timeout}
ansible_managed = {self.config.ansible.managed_banner}
roles_path = {self.config.ansible.galaxy_roles_dir}

[ssh_connection]
scp_if_ssh = {"True" if self.config.ansible.scp_if_ssh else "False"}
"""
        
        log_info(f"Creating ansible.cfg: {config_path}")
        
        if self.config.dry_run:
            log_info(f"DRY RUN: Would create ansible.cfg with content:")
            print(config_content)
            return True
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            log_info("ansible.cfg created successfully")
            return True
        except Exception as e:
            log_warning(f"Failed to create ansible.cfg: {e}")
            return False
