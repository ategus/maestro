"""
Template engine for Pyestro project generation.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from jinja2 import Environment, FileSystemLoader, Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

from .validation import InputValidator


class TemplateEngine:
    """Template engine for generating Pyestro projects."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize template engine."""
        if templates_dir is None:
            # Default to templates directory in package
            templates_dir = Path(__file__).parent.parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.validator = InputValidator()
        
        # Initialize Jinja2 if available
        if HAS_JINJA2:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.jinja_env = None
    
    def get_available_templates(self) -> List[str]:
        """Get list of available project templates."""
        if not self.templates_dir.exists():
            return []
        
        templates = []
        for item in self.templates_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it has a template.json metadata file
                metadata_file = item / "template.json"
                if metadata_file.exists():
                    templates.append(item.name)
        
        return sorted(templates)
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template metadata information."""
        template_dir = self.templates_dir / template_name
        metadata_file = template_dir / "template.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def validate_project_name(self, name: str) -> bool:
        """Validate project name."""
        if not name:
            return False
        
        # Check for valid filename characters
        if not self.validator.validate_path_component(name):
            return False
        
        # Additional checks for project names
        if name.startswith('.') or name.startswith('-'):
            return False
        
        if len(name) > 100:  # Reasonable length limit
            return False
        
        return True
    
    def render_template_content(self, content: str, variables: Dict[str, Any]) -> str:
        """Render template content with variables."""
        if not HAS_JINJA2:
            # Simple variable substitution without Jinja2
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                content = content.replace(placeholder, str(value))
            return content
        
        # Use Jinja2 for advanced templating
        template = Template(content)
        return template.render(**variables)
    
    def render_file_template(self, template_path: Path, variables: Dict[str, Any]) -> str:
        """Render a template file with variables."""
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.render_template_content(content, variables)
    
    def create_project(self, template_name: str, project_name: str, 
                      target_dir: Path, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new project from template."""
        if not self.validate_project_name(project_name):
            raise ValueError(f"Invalid project name: {project_name}")
        
        template_dir = self.templates_dir / template_name
        if not template_dir.exists():
            raise ValueError(f"Template '{template_name}' not found")
        
        # Get template metadata
        template_info = self.get_template_info(template_name)
        if not template_info:
            raise ValueError(f"Template '{template_name}' has no metadata")
        
        # Prepare variables
        if variables is None:
            variables = {}
        
        # Add default variables
        variables.update({
            'project_name': project_name,
            'project_dir': str(target_dir),
            'template_name': template_name
        })
        
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Process template files
        success = True
        try:
            self._process_template_directory(template_dir, target_dir, variables)
        except Exception as e:
            print(f"Error creating project: {e}")
            success = False
        
        return success
    
    def _process_template_directory(self, template_dir: Path, target_dir: Path, 
                                   variables: Dict[str, Any]) -> None:
        """Recursively process template directory."""
        for item in template_dir.iterdir():
            # Skip metadata and hidden files
            if item.name in ('template.json', '.gitkeep') or item.name.startswith('.'):
                continue
            
            # Calculate target path
            target_name = self.render_template_content(item.name, variables)
            target_path = target_dir / target_name
            
            if item.is_dir():
                # Recursively process subdirectory
                target_path.mkdir(parents=True, exist_ok=True)
                self._process_template_directory(item, target_path, variables)
            else:
                # Process file
                self._process_template_file(item, target_path, variables)
    
    def _process_template_file(self, template_file: Path, target_file: Path, 
                              variables: Dict[str, Any]) -> None:
        """Process a single template file."""
        if template_file.suffix in ('.j2', '.jinja', '.template'):
            # Render template file
            content = self.render_file_template(template_file, variables)
            
            # Remove template extension from target filename
            if target_file.suffix in ('.j2', '.jinja', '.template'):
                target_file = target_file.with_suffix('')
            
            # Write rendered content
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            # Copy binary/non-template file as-is
            shutil.copy2(template_file, target_file)


class ProjectGenerator:
    """High-level project generator interface."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize project generator."""
        self.template_engine = TemplateEngine(templates_dir)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List available templates with their information."""
        templates = []
        for template_name in self.template_engine.get_available_templates():
            info = self.template_engine.get_template_info(template_name)
            if info:
                templates.append({
                    'name': template_name,
                    **info
                })
        return templates
    
    def create_project(self, template_name: str, project_name: str, 
                      target_dir: Optional[Path] = None, 
                      variables: Optional[Dict[str, Any]] = None,
                      dry_run: bool = False) -> bool:
        """Create a new project from template."""
        if target_dir is None:
            target_dir = Path.cwd() / project_name
        
        if dry_run:
            print(f"Would create project '{project_name}' using template '{template_name}' in {target_dir}")
            return True
        
        try:
            return self.template_engine.create_project(
                template_name, project_name, target_dir, variables
            )
        except Exception as e:
            print(f"Failed to create project: {e}")
            return False
    
    def interactive_create(self) -> bool:
        """Interactive project creation wizard."""
        print("Pyestro Project Creation Wizard")
        print("=" * 35)
        
        # Show available templates
        templates = self.list_templates()
        if not templates:
            print("No templates available!")
            return False
        
        print("\nAvailable templates:")
        for i, template in enumerate(templates, 1):
            description = template.get('description', 'No description')
            print(f"  {i}. {template['name']} - {description}")
        
        # Get template selection
        try:
            choice = input(f"\nSelect template (1-{len(templates)}): ").strip()
            template_idx = int(choice) - 1
            if template_idx < 0 or template_idx >= len(templates):
                raise ValueError("Invalid choice")
            
            selected_template = templates[template_idx]
            template_name = selected_template['name']
        except (ValueError, KeyboardInterrupt):
            print("Invalid selection or cancelled.")
            return False
        
        # Get project name
        try:
            project_name = input("Project name: ").strip()
            if not self.template_engine.validate_project_name(project_name):
                print("Invalid project name!")
                return False
        except KeyboardInterrupt:
            print("Cancelled.")
            return False
        
        # Get target directory
        try:
            target_input = input(f"Target directory (default: ./{project_name}): ").strip()
            if target_input:
                target_dir = Path(target_input)
            else:
                target_dir = Path.cwd() / project_name
        except KeyboardInterrupt:
            print("Cancelled.")
            return False
        
        # Collect template variables
        variables = {}
        template_vars = selected_template.get('variables', {})
        
        if template_vars:
            print(f"\nTemplate '{template_name}' configuration:")
            for var_name, var_info in template_vars.items():
                try:
                    prompt = var_info.get('prompt', f"{var_name}")
                    default = var_info.get('default', '')
                    
                    if default:
                        user_input = input(f"  {prompt} (default: {default}): ").strip()
                        value = user_input if user_input else default
                    else:
                        value = input(f"  {prompt}: ").strip()
                    
                    variables[var_name] = value
                except KeyboardInterrupt:
                    print("Cancelled.")
                    return False
        
        # Confirm creation
        print(f"\nProject Summary:")
        print(f"  Template: {template_name}")
        print(f"  Name: {project_name}")
        print(f"  Directory: {target_dir}")
        if variables:
            print(f"  Variables: {variables}")
        
        try:
            confirm = input("\nCreate project? (y/N): ").strip().lower()
            if confirm not in ('y', 'yes'):
                print("Cancelled.")
                return False
        except KeyboardInterrupt:
            print("Cancelled.")
            return False
        
        # Create the project
        return self.create_project(template_name, project_name, target_dir, variables)