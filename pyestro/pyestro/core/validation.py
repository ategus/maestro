"""
Input validation and sanitization for Pyestro.
"""

import re
from pathlib import Path
from typing import Any, List, Optional
from urllib.parse import urlparse


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class InputValidator:
    """Validates and sanitizes user inputs."""
    
    # Hostname validation pattern (RFC 1123)
    HOSTNAME_PATTERN = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    # Node name pattern (alphanumeric, dots, hyphens, underscores)
    NODE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
    
    # Shell command blacklist (dangerous characters)
    SHELL_BLACKLIST = re.compile(r'[;&|`$\(\)<>]')
    
    @staticmethod
    def sanitize_hostname(hostname: str) -> str:
        """Validate and sanitize hostnames."""
        if not hostname or not isinstance(hostname, str):
            raise ValidationError("Hostname must be a non-empty string")
        
        hostname = hostname.strip().lower()
        
        if not InputValidator.HOSTNAME_PATTERN.match(hostname):
            raise ValidationError(f"Invalid hostname format: {hostname}")
        
        if len(hostname) > 253:
            raise ValidationError(f"Hostname too long: {hostname}")
        
        return hostname
    
    @staticmethod
    def sanitize_node_name(node_name: str) -> str:
        """Validate and sanitize node names."""
        if not node_name or not isinstance(node_name, str):
            raise ValidationError("Node name must be a non-empty string")
        
        node_name = node_name.strip()
        
        if not InputValidator.NODE_NAME_PATTERN.match(node_name):
            raise ValidationError(f"Invalid node name format: {node_name}")
        
        if len(node_name) > 100:
            raise ValidationError(f"Node name too long: {node_name}")
        
        return node_name
    
    @staticmethod
    def validate_path(path: str, must_exist: bool = True) -> Path:
        """Validate file paths."""
        if not path or not isinstance(path, str):
            raise ValidationError("Path must be a non-empty string")
        
        try:
            p = Path(path).expanduser().resolve()
        except Exception as e:
            raise ValidationError(f"Invalid path format: {path} - {e}")
        
        # Check for path traversal attempts
        if '..' in Path(path).parts:
            raise ValidationError(f"Path traversal not allowed: {path}")
        
        if must_exist and not p.exists():
            raise ValidationError(f"Path does not exist: {path}")
        
        return p
    
    @staticmethod
    def validate_path_component(component: str) -> bool:
        """Validate a single path component (filename/directory name)."""
        if not component or not isinstance(component, str):
            return False
        
        component = component.strip()
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*\0'
        if any(char in component for char in invalid_chars):
            return False
        
        # Check for reserved names on Windows
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        if component.upper() in reserved_names:
            return False
        
        # Check for path traversal
        if component in ('.', '..'):
            return False
        
        # Check length (most filesystems have 255 byte limit)
        if len(component.encode('utf-8')) > 255:
            return False
        
        return True
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URLs."""
        if not url or not isinstance(url, str):
            raise ValidationError("URL must be a non-empty string")
        
        url = url.strip()
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(f"Invalid URL format: {url} - {e}")
        
        # Check scheme
        allowed_schemes = {'http', 'https', 'git', 'ssh'}
        if parsed.scheme not in allowed_schemes and not url.startswith('git@'):
            raise ValidationError(f"Unsupported URL scheme: {parsed.scheme}")
        
        # Basic hostname validation for non-SSH URLs
        if parsed.scheme in {'http', 'https', 'git'} and not parsed.netloc:
            raise ValidationError(f"URL missing hostname: {url}")
        
        return url
    
    @staticmethod
    def sanitize_shell_input(input_str: str) -> str:
        """Sanitize input to prevent shell injection."""
        if not isinstance(input_str, str):
            raise ValidationError("Input must be a string")
        
        if InputValidator.SHELL_BLACKLIST.search(input_str):
            raise ValidationError(f"Input contains dangerous characters: {input_str}")
        
        return input_str.strip()
    
    @staticmethod
    def validate_ansible_module_name(module_name: str) -> str:
        """Validate Ansible module names."""
        if not module_name or not isinstance(module_name, str):
            raise ValidationError("Module name must be a non-empty string")
        
        module_name = module_name.strip()
        
        # Ansible module names can contain letters, numbers, underscores, and dots
        if not re.match(r'^[a-zA-Z0-9_.]+$', module_name):
            raise ValidationError(f"Invalid Ansible module name: {module_name}")
        
        return module_name
    
    @staticmethod
    def validate_filter_pattern(pattern: str) -> str:
        """Validate filter patterns for nodes, classes, etc."""
        if not isinstance(pattern, str):
            raise ValidationError("Filter pattern must be a string")
        
        pattern = pattern.strip()
        
        if not pattern:
            raise ValidationError("Filter pattern cannot be empty")
        
        # Allow alphanumeric, wildcards, dots, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9.*_-]+$', pattern):
            raise ValidationError(f"Invalid filter pattern: {pattern}")
        
        return pattern
    
    @staticmethod
    def validate_config_dict(config_dict: dict) -> dict:
        """Validate configuration dictionary."""
        if not isinstance(config_dict, dict):
            raise ValidationError("Configuration must be a dictionary")
        
        # Validate required string fields
        string_fields = ['maestro_dir', 'work_dir']
        for field in string_fields:
            if field in config_dict:
                if not isinstance(config_dict[field], str):
                    raise ValidationError(f"Field {field} must be a string")
        
        # Validate repository URLs
        if 'repositories' in config_dict:
            if not isinstance(config_dict['repositories'], dict):
                raise ValidationError("repositories must be a dictionary")
            
            for name, url in config_dict['repositories'].items():
                InputValidator.validate_url(url)
        
        # Validate directory mappings
        for dir_field in ['inventory_dirs', 'playbook_dirs', 'local_dirs']:
            if dir_field in config_dict:
                if not isinstance(config_dict[dir_field], dict):
                    raise ValidationError(f"{dir_field} must be a dictionary")
                
                for name, path in config_dict[dir_field].items():
                    if not isinstance(path, str):
                        raise ValidationError(f"Path in {dir_field}.{name} must be a string")
        
        return config_dict
    
    @staticmethod
    def sanitize_command_args(args: List[str]) -> List[str]:
        """Sanitize command arguments."""
        if not isinstance(args, list):
            raise ValidationError("Arguments must be a list")
        
        sanitized = []
        for arg in args:
            if not isinstance(arg, str):
                raise ValidationError("All arguments must be strings")
            
            # Check for dangerous characters
            if InputValidator.SHELL_BLACKLIST.search(arg):
                raise ValidationError(f"Argument contains dangerous characters: {arg}")
            
            sanitized.append(arg.strip())
        
        return sanitized
