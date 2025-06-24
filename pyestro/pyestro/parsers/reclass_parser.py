"""
Reclass integration for Pyestro.
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from ..core.config import log_info, log_warning
from ..core.validation import InputValidator, ValidationError


class ReclassManager:
    """Manages reclass operations and parsing."""
    
    def __init__(self, inventory_dir: Path, dry_run: bool = True):
        self.inventory_dir = inventory_dir
        self.dry_run = dry_run
        self.reclass_path = self._find_reclass()
    
    def _find_reclass(self) -> Optional[str]:
        """Find reclass executable."""
        reclass_path = shutil.which("reclass")
        if not reclass_path:
            log_warning("reclass executable not found in PATH")
        return reclass_path
    
    def get_node_data(self, node_name: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific node from reclass."""
        if not self.reclass_path:
            log_warning("reclass not available")
            return None
        
        try:
            node_name = InputValidator.sanitize_node_name(node_name)
        except ValidationError as e:
            log_warning(f"Invalid node name: {e}")
            return None
        
        cmd = [
            self.reclass_path,
            "-b", str(self.inventory_dir),
            "-n", node_name,
            "--output", "json"
        ]
        
        log_info(f"Getting data for node: {node_name}")
        
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
    
    def get_inventory_data(self) -> Optional[Dict[str, Any]]:
        """Get complete inventory data from reclass."""
        if not self.reclass_path:
            log_warning("reclass not available")
            return None
        
        cmd = [
            self.reclass_path,
            "-b", str(self.inventory_dir),
            "--inventory",
            "--output", "json"
        ]
        
        log_info("Getting inventory data")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return {"nodes": {}, "classes": {}}
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            log_warning(f"reclass inventory failed: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            log_warning(f"Failed to parse reclass inventory output: {e}")
            return None
    
    def list_nodes(self) -> List[str]:
        """List all available nodes."""
        inventory_data = self.get_inventory_data()
        if inventory_data and "nodes" in inventory_data:
            return list(inventory_data["nodes"].keys())
        return []
    
    def list_classes(self) -> List[str]:
        """List all available classes."""
        inventory_data = self.get_inventory_data()
        if inventory_data and "classes" in inventory_data:
            return list(inventory_data["classes"].keys())
        return []
    
    def get_node_parameters(self, node_name: str) -> Dict[str, Any]:
        """Get parameters for a specific node."""
        node_data = self.get_node_data(node_name)
        if node_data and "parameters" in node_data:
            return node_data["parameters"]
        return {}
    
    def get_node_classes(self, node_name: str) -> List[str]:
        """Get classes for a specific node."""
        node_data = self.get_node_data(node_name)
        if node_data and "classes" in node_data:
            return node_data["classes"]
        return []
    
    def get_nodes_by_class(self, class_name: str) -> List[str]:
        """Get all nodes that use a specific class."""
        inventory_data = self.get_inventory_data()
        if not inventory_data or "nodes" not in inventory_data:
            return []
        
        matching_nodes = []
        for node_name, node_data in inventory_data["nodes"].items():
            if "classes" in node_data and class_name in node_data["classes"]:
                matching_nodes.append(node_name)
        
        return matching_nodes
    
    def search_parameter(self, parameter_path: str) -> Dict[str, Any]:
        """Search for a parameter across all nodes."""
        inventory_data = self.get_inventory_data()
        if not inventory_data or "nodes" not in inventory_data:
            return {}
        
        results = {}
        path_parts = parameter_path.split(":")
        
        for node_name, node_data in inventory_data["nodes"].items():
            if "parameters" not in node_data:
                continue
            
            # Navigate through parameter path
            current = node_data["parameters"]
            try:
                for part in path_parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        current = None
                        break
                
                if current is not None:
                    results[node_name] = current
            except (KeyError, TypeError):
                continue
        
        return results
    
    def validate_inventory(self) -> List[str]:
        """Validate the reclass inventory and return any errors."""
        errors = []
        
        if not self.inventory_dir.exists():
            errors.append(f"Inventory directory does not exist: {self.inventory_dir}")
            return errors
        
        if not self.reclass_path:
            errors.append("reclass executable not found")
            return errors
        
        # Try to get inventory data
        inventory_data = self.get_inventory_data()
        if inventory_data is None:
            errors.append("Failed to load inventory data from reclass")
        
        # Check for required subdirectories
        required_dirs = ["nodes", "classes"]
        for dir_name in required_dirs:
            dir_path = self.inventory_dir / dir_name
            if not dir_path.exists():
                errors.append(f"Required directory missing: {dir_path}")
        
        return errors
    
    def filter_nodes(
        self,
        node_filter: Optional[str] = None,
        class_filter: Optional[str] = None,
        project_filter: Optional[str] = None
    ) -> List[str]:
        """Filter nodes based on various criteria."""
        all_nodes = self.list_nodes()
        
        if not any([node_filter, class_filter, project_filter]):
            return all_nodes
        
        filtered_nodes = set(all_nodes)
        
        # Apply node filter
        if node_filter:
            try:
                node_filter = InputValidator.validate_filter_pattern(node_filter)
                if "*" in node_filter:
                    # Simple wildcard matching
                    pattern = node_filter.replace("*", ".*")
                    import re
                    regex = re.compile(pattern)
                    filtered_nodes = {n for n in filtered_nodes if regex.match(n)}
                else:
                    # Exact match
                    filtered_nodes = {n for n in filtered_nodes if n == node_filter}
            except ValidationError as e:
                log_warning(f"Invalid node filter: {e}")
        
        # Apply class filter
        if class_filter:
            try:
                class_filter = InputValidator.validate_filter_pattern(class_filter)
                nodes_with_class = set(self.get_nodes_by_class(class_filter))
                filtered_nodes = filtered_nodes.intersection(nodes_with_class)
            except ValidationError as e:
                log_warning(f"Invalid class filter: {e}")
        
        # Apply project filter (assuming project is a parameter)
        if project_filter:
            try:
                project_filter = InputValidator.validate_filter_pattern(project_filter)
                project_nodes = set()
                for node in filtered_nodes:
                    params = self.get_node_parameters(node)
                    if params.get("project") == project_filter:
                        project_nodes.add(node)
                filtered_nodes = project_nodes
            except ValidationError as e:
                log_warning(f"Invalid project filter: {e}")
        
        return sorted(list(filtered_nodes))
