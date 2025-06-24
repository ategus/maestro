"""
Reclass integration for Pyestro.
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..core.config import log_info, log_warning
from ..core.validation import InputValidator


class ReclassParser:
    """Handles reclass operations and parsing."""
    
    def __init__(self, inventory_dir: Path, dry_run: bool = True):
        self.inventory_dir = inventory_dir
        self.dry_run = dry_run
        self.reclass_path = self._find_reclass()
    
    def _find_reclass(self) -> Optional[str]:
        """Find reclass executable."""
        reclass_path = shutil.which("reclass")
        if not reclass_path:
            log_warning("reclass executable not found, some functionality will be limited")
        return reclass_path
    
    def get_node_data(self, node_name: str) -> Optional[Dict[str, Any]]:
        """Get node data from reclass."""
        if not self.reclass_path:
            log_warning("reclass not available, cannot get node data")
            return None
        
        # Validate node name
        try:
            node_name = InputValidator.sanitize_node_name(node_name)
        except Exception as e:
            log_warning(f"Invalid node name: {e}")
            return None
        
        cmd = [
            self.reclass_path,
            '-b', str(self.inventory_dir),
            '-n', node_name,
            '--output-format', 'json'
        ]
        
        log_info(f"Getting node data for: {node_name}")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return {"parameters": {}, "classes": [], "applications": []}
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            log_warning(f"reclass failed for node {node_name}: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            log_warning(f"Failed to parse reclass output for node {node_name}: {e}")
            return None
    
    def list_nodes(self) -> List[str]:
        """List all available nodes."""
        if not self.reclass_path:
            # Fallback: scan inventory directory
            return self._scan_nodes_from_filesystem()
        
        cmd = [
            self.reclass_path,
            '-b', str(self.inventory_dir),
            '--inventory'
        ]
        
        log_info("Listing available nodes")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return ["example-node1", "example-node2"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse reclass inventory output
            inventory = json.loads(result.stdout)
            nodes = list(inventory.get('nodes', {}).keys())
            return sorted(nodes)
        except subprocess.CalledProcessError as e:
            log_warning(f"reclass inventory failed: {e.stderr}")
            return self._scan_nodes_from_filesystem()
        except json.JSONDecodeError as e:
            log_warning(f"Failed to parse reclass inventory: {e}")
            return self._scan_nodes_from_filesystem()
    
    def _scan_nodes_from_filesystem(self) -> List[str]:
        """Scan nodes directory for node files."""
        nodes_dir = self.inventory_dir / "nodes"
        if not nodes_dir.exists():
            return []
        
        nodes = []
        for node_file in nodes_dir.rglob("*.yml"):
            # Convert path to node name
            rel_path = node_file.relative_to(nodes_dir)
            node_name = str(rel_path.with_suffix(''))
            nodes.append(node_name.replace('/', '.'))
        
        return sorted(nodes)
    
    def get_node_parameters(self, node_name: str) -> Dict[str, Any]:
        """Get parameters for a specific node."""
        node_data = self.get_node_data(node_name)
        if node_data:
            return node_data.get('parameters', {})
        return {}
    
    def get_node_classes(self, node_name: str) -> List[str]:
        """Get classes for a specific node."""
        node_data = self.get_node_data(node_name)
        if node_data:
            return node_data.get('classes', [])
        return []
    
    def search_parameter(self, parameter_name: str) -> Dict[str, Any]:
        """Search for a parameter across all nodes."""
        nodes = self.list_nodes()
        results = {}
        
        for node in nodes:
            parameters = self.get_node_parameters(node)
            if parameter_name in parameters:
                results[node] = parameters[parameter_name]
        
        return results
    
    def validate_inventory(self) -> bool:
        """Validate the reclass inventory."""
        if not self.inventory_dir.exists():
            log_warning(f"Inventory directory does not exist: {self.inventory_dir}")
            return False
        
        required_dirs = ['nodes', 'classes']
        for dirname in required_dirs:
            dir_path = self.inventory_dir / dirname
            if not dir_path.exists():
                log_warning(f"Required directory missing: {dir_path}")
                return False
        
        # Check if we can list nodes
        nodes = self.list_nodes()
        if not nodes:
            log_warning("No nodes found in inventory")
            return False
        
        log_info(f"Inventory validation passed. Found {len(nodes)} nodes.")
        return True
    
    def merge_inventories(self, source_dirs: List[Path], target_dir: Path) -> bool:
        """Merge multiple inventory directories."""
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Create required subdirectories
        (target_dir / "nodes").mkdir(exist_ok=True)
        (target_dir / "classes").mkdir(exist_ok=True)
        
        log_info(f"Merging {len(source_dirs)} inventory directories into {target_dir}")
        
        success = True
        for source_dir in source_dirs:
            if not source_dir.exists():
                log_warning(f"Source inventory directory does not exist: {source_dir}")
                continue
            
            # Copy nodes and classes
            for subdir in ['nodes', 'classes']:
                source_subdir = source_dir / subdir
                target_subdir = target_dir / subdir
                
                if source_subdir.exists():
                    from ..core.file_ops import FileManager
                    file_manager = FileManager(self.dry_run)
                    result = file_manager.sync_directories(source_subdir, target_subdir)
                    success = success and result
        
        return success
