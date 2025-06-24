"""
File operations and synchronization for Pyestro.
"""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from ..core.config import log_info, log_warning


class FileManager:
    """Manages file operations and synchronization."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.rsync_path = self._find_rsync()
    
    def _find_rsync(self) -> Optional[str]:
        """Find rsync executable."""
        rsync_path = shutil.which("rsync")
        if not rsync_path:
            log_warning("rsync executable not found, falling back to Python copy")
        return rsync_path
    
    def sync_directories(
        self,
        source: Path,
        destination: Path,
        options: str = "-a -m --exclude=.keep",
        recursive: bool = True
    ) -> bool:
        """Synchronize directories using rsync or Python fallback."""
        
        if not source.exists():
            log_warning(f"Source directory does not exist: {source}")
            return False
        
        destination.mkdir(parents=True, exist_ok=True)
        
        if self.rsync_path:
            return self._rsync_sync(source, destination, options)
        else:
            return self._python_sync(source, destination, recursive)
    
    def _rsync_sync(self, source: Path, destination: Path, options: str) -> bool:
        """Synchronize using rsync."""
        if not self.rsync_path:
            return False
        
        # Parse rsync options
        option_list = options.split()
        
        # Ensure source ends with / for rsync
        source_str = str(source)
        if not source_str.endswith("/"):
            source_str += "/"
        
        cmd = [self.rsync_path] + option_list + [source_str, str(destination)]
        
        log_info(f"Syncing {source} to {destination} using rsync")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return True
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            log_info(f"Successfully synced {source} to {destination}")
            return True
        except subprocess.CalledProcessError as e:
            log_warning(f"rsync failed: {e.stderr}")
            return False
    
    def _python_sync(self, source: Path, destination: Path, recursive: bool) -> bool:
        """Synchronize using Python's shutil (fallback)."""
        log_info(f"Syncing {source} to {destination} using Python")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would copy {source} to {destination}")
            return True
        
        try:
            if source.is_file():
                shutil.copy2(source, destination)
            elif source.is_dir() and recursive:
                # Copy directory contents
                for item in source.rglob("*") if recursive else source.iterdir():
                    if item.name.startswith('.') and item.name in ['.git', '.keep']:
                        continue
                    
                    rel_path = item.relative_to(source)
                    dest_path = destination / rel_path
                    
                    if item.is_file():
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
                    elif item.is_dir():
                        dest_path.mkdir(parents=True, exist_ok=True)
            
            log_info(f"Successfully synced {source} to {destination}")
            return True
        except Exception as e:
            log_warning(f"Python sync failed: {e}")
            return False
    
    def merge_directories(self, source_dirs: List[Path], target_dir: Path) -> bool:
        """Merge multiple source directories into target directory."""
        target_dir.mkdir(parents=True, exist_ok=True)
        
        log_info(f"Merging {len(source_dirs)} directories into {target_dir}")
        
        success = True
        for source_dir in source_dirs:
            if source_dir.exists():
                result = self.sync_directories(source_dir, target_dir)
                success = success and result
            else:
                log_warning(f"Source directory does not exist: {source_dir}")
        
        return success
    
    def backup_file(self, file_path: Path, backup_suffix: str = ".backup") -> bool:
        """Create a backup of a file."""
        if not file_path.exists():
            log_warning(f"Cannot backup non-existent file: {file_path}")
            return False
        
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
        
        log_info(f"Creating backup: {file_path} -> {backup_path}")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would create backup {backup_path}")
            return True
        
        try:
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            log_warning(f"Failed to create backup: {e}")
            return False
    
    def ensure_directory(self, dir_path: Path) -> bool:
        """Ensure directory exists."""
        if dir_path.exists():
            return True
        
        log_info(f"Creating directory: {dir_path}")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would create directory {dir_path}")
            return True
        
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            log_warning(f"Failed to create directory {dir_path}: {e}")
            return False
    
    def remove_file(self, file_path: Path) -> bool:
        """Remove a file."""
        if not file_path.exists():
            return True
        
        log_info(f"Removing file: {file_path}")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would remove file {file_path}")
            return True
        
        try:
            file_path.unlink()
            return True
        except Exception as e:
            log_warning(f"Failed to remove file {file_path}: {e}")
            return False
    
    def remove_directory(self, dir_path: Path) -> bool:
        """Remove a directory and its contents."""
        if not dir_path.exists():
            return True
        
        log_info(f"Removing directory: {dir_path}")
        
        if self.dry_run:
            log_info(f"DRY RUN: Would remove directory {dir_path}")
            return True
        
        try:
            shutil.rmtree(dir_path)
            return True
        except Exception as e:
            log_warning(f"Failed to remove directory {dir_path}: {e}")
            return False
