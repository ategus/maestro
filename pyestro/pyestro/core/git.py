"""
Git operations for Pyestro.
"""

import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
from ..core.config import RepositoryConfig, log_info, log_warning


class GitManager:
    """Manages Git operations for repositories."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.git_path = self._find_git()
    
    def _find_git(self) -> Optional[str]:
        """Find git executable."""
        git_path = shutil.which("git")
        if not git_path:
            log_warning("Git executable not found in PATH")
        return git_path
    
    def clone_repository(self, repo_config: RepositoryConfig, target_dir: Path) -> bool:
        """Clone a Git repository."""
        if not self.git_path:
            log_warning(f"Cannot clone {repo_config.name}: Git not available")
            return False
        
        if target_dir.exists() and (target_dir / ".git").exists():
            log_info(f"Repository {repo_config.name} already exists, pulling updates")
            return self.pull_repository(target_dir)
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.git_path,
            "clone",
            repo_config.url,
            str(target_dir)
        ]
        
        if repo_config.branch != "main":
            cmd.extend(["--branch", repo_config.branch])
        
        log_info(f"Cloning repository {repo_config.name} from {repo_config.url}")
        
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
            log_info(f"Successfully cloned {repo_config.name}")
            return True
        except subprocess.CalledProcessError as e:
            log_warning(f"Failed to clone {repo_config.name}: {e.stderr}")
            return False
    
    def pull_repository(self, repo_dir: Path) -> bool:
        """Pull updates for an existing repository."""
        if not self.git_path:
            log_warning(f"Cannot pull {repo_dir}: Git not available")
            return False
        
        if not (repo_dir / ".git").exists():
            log_warning(f"Directory {repo_dir} is not a Git repository")
            return False
        
        cmd = [self.git_path, "-C", str(repo_dir), "pull"]
        
        log_info(f"Pulling updates for repository in {repo_dir}")
        
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
            log_info(f"Successfully pulled updates for {repo_dir}")
            return True
        except subprocess.CalledProcessError as e:
            log_warning(f"Failed to pull updates for {repo_dir}: {e.stderr}")
            return False
    
    def get_repository_status(self, repo_dir: Path) -> Optional[dict]:
        """Get status information for a repository."""
        if not self.git_path or not (repo_dir / ".git").exists():
            return None
        
        try:
            # Get current branch
            branch_result = subprocess.run(
                [self.git_path, "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            branch = branch_result.stdout.strip()
            
            # Get last commit hash
            commit_result = subprocess.run(
                [self.git_path, "-C", str(repo_dir), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = commit_result.stdout.strip()[:8]
            
            # Check if there are uncommitted changes
            status_result = subprocess.run(
                [self.git_path, "-C", str(repo_dir), "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            has_changes = bool(status_result.stdout.strip())
            
            return {
                "branch": branch,
                "commit": commit_hash,
                "has_changes": has_changes,
                "path": str(repo_dir)
            }
        except subprocess.CalledProcessError:
            return None
    
    def clone_repositories(self, repo_configs: List[RepositoryConfig], base_dir: Path) -> dict:
        """Clone multiple repositories."""
        results = {}
        
        for repo_config in repo_configs:
            target_dir = base_dir / repo_config.name
            success = self.clone_repository(repo_config, target_dir)
            results[repo_config.name] = {
                "success": success,
                "path": target_dir
            }
        
        return results
