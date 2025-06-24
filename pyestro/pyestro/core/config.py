"""
Core configuration management for Pyestro.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Simple logging until we have proper dependencies
def log_info(msg: str, **kwargs: Any) -> None:
    print(f"INFO: {msg}", kwargs if kwargs else "")

def log_warning(msg: str, **kwargs: Any) -> None:
    print(f"WARNING: {msg}", kwargs if kwargs else "")


class RepositoryConfig:
    """Configuration for Git repositories."""
    
    def __init__(self, name: str, url: str, branch: str = "main", verify_ssl: bool = True):
        self.name = name
        self.url = url
        self.branch = branch
        self.verify_ssl = verify_ssl


class AnsibleConfig:
    """Ansible-specific configuration."""
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        managed_banner: str = "Ansible managed. All local changes will be lost!",
        timeout: int = 60,
        scp_if_ssh: bool = True,
        galaxy_roles_dir: str = ".ansible-galaxy-roles"
    ):
        self.config_file = config_file
        self.managed_banner = managed_banner
        self.timeout = timeout
        self.scp_if_ssh = scp_if_ssh
        self.galaxy_roles_dir = galaxy_roles_dir


class MaestroConfig:
    """Main Pyestro configuration."""
    
    def __init__(
        self,
        maestro_dir: Optional[Union[str, Path]] = None,
        work_dir: Union[str, Path] = "./workdir",
        dry_run: bool = True,
        verbose: int = 1,
        force: bool = False,
        repositories: Optional[Dict[str, str]] = None,
        inventory_dirs: Optional[Dict[str, str]] = None,
        playbook_dirs: Optional[Dict[str, str]] = None,
        local_dirs: Optional[Dict[str, str]] = None,
        ansible: Optional[AnsibleConfig] = None,
        rsync_options: str = "-a -m --exclude=.keep",
        node_filter: Optional[str] = None,
        class_filter: Optional[str] = None,
        project_filter: Optional[str] = None,
        **kwargs: Any
    ):
        # Core directories
        self.maestro_dir = Path(maestro_dir or Path.cwd()).expanduser().resolve()
        self.work_dir = Path(work_dir).expanduser().resolve()
        
        # Behavior settings
        self.dry_run = dry_run
        self.verbose = verbose
        self.force = force
        
        # Repository configuration
        self.repositories = repositories or {}
        
        # Directory mappings
        self.inventory_dirs = inventory_dirs or {}
        self.playbook_dirs = playbook_dirs or {}
        self.local_dirs = local_dirs or {}
        
        # Tool configuration
        self.ansible = ansible or AnsibleConfig()
        
        # Rsync options
        self.rsync_options = rsync_options
        
        # Filtering
        self.node_filter = node_filter
        self.class_filter = class_filter
        self.project_filter = project_filter
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate configuration."""
        # Validate repository URLs
        for name, url in self.repositories.items():
            if not url or not isinstance(url, str):
                raise ValueError(f"Invalid repository URL for {name}: {url}")
            # Basic URL validation
            if not (url.startswith(('http://', 'https://', 'git://', 'ssh://')) or 
                   url.startswith('git@')):
                raise ValueError(f"Invalid repository URL format for {name}: {url}")
        
        # Validate directory mappings
        for mapping_name, mapping in [
            ("inventory_dirs", self.inventory_dirs),
            ("playbook_dirs", self.playbook_dirs),
            ("local_dirs", self.local_dirs)
        ]:
            for name, path in mapping.items():
                if not isinstance(path, str):
                    raise ValueError(f"Directory path must be string for {name} in {mapping_name}: {path}")
    
    @property
    def merged_inventory_dir(self) -> Path:
        """Get the merged inventory directory path."""
        return self.work_dir / "inventory"
    
    def get_repository_configs(self) -> List[RepositoryConfig]:
        """Get repository configurations."""
        configs = []
        for name, url in self.repositories.items():
            configs.append(RepositoryConfig(name=name, url=url))
        return configs
    
    def get_storage_dirs(self) -> List[Path]:
        """Get all storage directories."""
        dirs = []
        for path_str in self.inventory_dirs.values():
            if path_str and path_str != "none":
                dirs.append(Path(path_str))
        for path_str in self.local_dirs.values():
            if path_str and path_str != "none":
                dirs.append(Path(path_str))
        return dirs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'maestro_dir': str(self.maestro_dir),
            'work_dir': str(self.work_dir),
            'dry_run': self.dry_run,
            'verbose': self.verbose,
            'force': self.force,
            'repositories': self.repositories,
            'inventory_dirs': self.inventory_dirs,
            'playbook_dirs': self.playbook_dirs,
            'local_dirs': self.local_dirs,
            'ansible': {
                'config_file': self.ansible.config_file,
                'managed_banner': self.ansible.managed_banner,
                'timeout': self.ansible.timeout,
                'scp_if_ssh': self.ansible.scp_if_ssh,
                'galaxy_roles_dir': self.ansible.galaxy_roles_dir,
            },
            'rsync_options': self.rsync_options,
            'node_filter': self.node_filter,
            'class_filter': self.class_filter,
            'project_filter': self.project_filter,
        }


class ConfigManager:
    """Manages Pyestro configuration loading and validation."""
    
    DEFAULT_CONFIG_NAMES = [
        "pyestro.yaml",
        "pyestro.yml",
        "pyestro.json",
        ".pyestro.yaml",
        ".pyestro.yml",
        ".pyestro.json",
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self._config: Optional[MaestroConfig] = None
    
    def load_config(self, config_path: Optional[Path] = None) -> MaestroConfig:
        """Load configuration from file or create default."""
        if config_path:
            self.config_path = config_path
        
        if not self.config_path:
            self.config_path = self._find_config_file()
        
        if self.config_path and self.config_path.exists():
            log_info("Loading configuration", path=str(self.config_path))
            return self._load_from_file(self.config_path)
        else:
            log_warning("No configuration file found, using defaults")
            return self._create_default_config()
    
    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in current directory."""
        cwd = Path.cwd()
        for name in self.DEFAULT_CONFIG_NAMES:
            config_path = cwd / name
            if config_path.exists():
                return config_path
        return None
    
    def _load_from_file(self, config_path: Path) -> MaestroConfig:
        """Load configuration from YAML/JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ('.yaml', '.yml'):
                    # For now, use JSON format until we add YAML dependency
                    raise ValueError("YAML support requires PyYAML. Please use JSON format or install dependencies.")
                else:
                    data = json.load(f)
            
            # Convert relative paths to absolute
            if 'maestro_dir' not in data:
                data['maestro_dir'] = str(config_path.parent)
            
            # Handle ansible configuration
            if 'ansible' in data and isinstance(data['ansible'], dict):
                ansible_data = data['ansible']
                data['ansible'] = AnsibleConfig(
                    config_file=ansible_data.get('config_file'),
                    managed_banner=ansible_data.get('managed_banner', "Ansible managed. All local changes will be lost!"),
                    timeout=ansible_data.get('timeout', 60),
                    scp_if_ssh=ansible_data.get('scp_if_ssh', True),
                    galaxy_roles_dir=ansible_data.get('galaxy_roles_dir', ".ansible-galaxy-roles")
                )
            
            self._config = MaestroConfig(**data)
            return self._config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading config file {config_path}: {e}")
    
    def _create_default_config(self) -> MaestroConfig:
        """Create default configuration."""
        default_data = {
            'maestro_dir': Path.cwd(),
            'repositories': {
                'maestro': 'https://github.com/inofix/maestro',
            },
            'inventory_dirs': {
                'main': './inventory',
            },
            'playbook_dirs': {
                'common_playbooks': './common_playbooks',
            },
            'local_dirs': {
                'any_confix': 'none',
                'packer_templates': 'none',
                'vagrant_boxes': 'none',
            }
        }
        self._config = MaestroConfig(**default_data)
        return self._config
    
    def save_config(self, config: MaestroConfig, config_path: Optional[Path] = None) -> None:
        """Save configuration to JSON file."""
        if not config_path:
            config_path = self.config_path or Path.cwd() / "pyestro.json"
        
        # Convert to serializable dict
        data = config.to_dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, sort_keys=True)
        
        log_info("Configuration saved", path=str(config_path))
    
    def migrate_from_bash(self, bash_config_path: Path) -> MaestroConfig:
        """Migrate configuration from bash .maestro file."""
        # This would parse bash associative arrays and convert to Python dict
        # For now, create a basic structure
        log_warning("Bash migration not fully implemented yet")
        return self._create_default_config()
    
    @property
    def config(self) -> MaestroConfig:
        """Get current configuration."""
        if not self._config:
            self._config = self.load_config()
        return self._config
