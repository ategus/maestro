"""
Main CLI entry point for Pyestro.
"""

import sys
from pathlib import Path
from typing import Optional

# Simple CLI without click dependency for now
from ..core.config import ConfigManager, MaestroConfig
from ..core.git import GitManager
from ..core.file_ops import FileManager
from ..core.templates import ProjectGenerator
from ..parsers.reclass_parser import ReclassManager
from ..integrations.ansible import AnsibleManager


def print_usage() -> None:
    """Print usage information."""
    print("""
Pyestro - Python Configuration Management Orchestrator

Usage: pyestro [options] command [arguments]

Commands:
  create <template> <name>  Create new project from template
  create --wizard           Interactive project creation wizard
  create --list             List available project templates
  init                      Initialize new project (legacy)
  setup                     Setup dependencies and clone repositories
  config show              Show current configuration
  config validate          Validate configuration
  nodes list               List all nodes
  nodes show <node>        Show detailed node information
  ansible <module> <args>  Execute ansible module
  ansible playbook <file>  Execute ansible playbook
  status                   Check host connectivity and repository status
  merge                    Merge storage directories
  search <pattern>         Search inventory and playbooks
  migrate --from-bash      Migrate from bash maestro
  git <subcommand>         Perform git operations

Options:
  -c, --config FILE      Configuration file path
  -v, --verbose          Verbose output (can be used multiple times)
  -n, --dry-run          Dry run mode
  -h, --help             Show this help message

Examples:
  pyestro create basic my-project        Create basic project
  pyestro create home-network my-home    Create home automation project
  pyestro create --wizard                Interactive project creation
  pyestro create --list                  Show available templates
  pyestro init                           Initialize legacy project
  pyestro config show
  pyestro nodes list
  pyestro ansible setup
  pyestro status
  pyestro git init
  pyestro git status
""")


def print_version() -> None:
    """Print version information."""
    from .. import __version__
    print(f"Pyestro {__version__}")


class CLI:
    """Simple CLI handler."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config: Optional[MaestroConfig] = None
        self.verbose = 0
        self.dry_run = False
    
    def parse_args(self, args: list[str]) -> tuple[str, list[str]]:
        """Parse command line arguments."""
        if not args:
            return "help", []
        
        # Handle global options
        filtered_args = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ('-h', '--help'):
                return "help", []
            elif arg in ('-V', '--version'):
                return "version", []
            elif arg in ('-v', '--verbose'):
                self.verbose += 1
            elif arg in ('-n', '--dry-run'):
                self.dry_run = True
            elif arg in ('-c', '--config'):
                if i + 1 < len(args):
                    config_path = Path(args[i + 1])
                    self.config_manager = ConfigManager(config_path)
                    i += 1  # Skip next argument
                else:
                    print("Error: --config requires a file path")
                    return "help", []
            else:
                filtered_args.append(arg)
            i += 1
        
        if not filtered_args:
            return "help", []
        
        command = filtered_args[0]
        command_args = filtered_args[1:]
        
        return command, command_args
    
    def load_config(self) -> None:
        """Load configuration."""
        self.config = self.config_manager.load_config()
        if self.dry_run:
            self.config.dry_run = True
        if self.verbose:
            self.config.verbose = self.verbose
    
    def cmd_init(self, args: list[str]) -> int:
        """Initialize new project."""
        print("Initializing new Pyestro project...")
        
        # Create default configuration
        config = self.config_manager._create_default_config()
        
        # Create default config file
        config_path = Path.cwd() / "pyestro.json"
        self.config_manager.save_config(config, config_path)
        
        # Create basic directory structure
        config.work_dir.mkdir(exist_ok=True)
        (config.work_dir / "inventory").mkdir(exist_ok=True)
        
        print(f"Created configuration file: {config_path}")
        print(f"Created work directory: {config.work_dir}")
        print("\nNext steps:")
        print("1. Edit pyestro.json to configure your repositories and directories")
        print("2. Run 'pyestro config validate' to check your configuration")
        print("3. Run 'pyestro nodes list' to see available nodes")
        
        return 0
    
    def cmd_config(self, args: list[str]) -> int:
        """Configuration management commands."""
        if not args:
            print("Error: config command requires subcommand (show, validate)")
            return 1
        
        subcommand = args[0]
        
        if subcommand == "show":
            self.load_config()
            if not self.config:
                print("Error: Could not load configuration")
                return 1
            
            print("Current configuration:")
            config_dict = self.config.to_dict()
            for key, value in config_dict.items():
                print(f"  {key}: {value}")
            return 0
        
        elif subcommand == "validate":
            try:
                self.load_config()
                print("Configuration is valid")
                return 0
            except Exception as e:
                print(f"Configuration validation failed: {e}")
                return 1
        
        else:
            print(f"Error: Unknown config subcommand: {subcommand}")
            return 1
    
    def cmd_nodes(self, args: list[str]) -> int:
        """Node management commands."""
        if not args:
            print("Error: nodes command requires subcommand (list)")
            return 1
        
        subcommand = args[0]
        
        if subcommand == "list":
            self.load_config()
            if not self.config:
                print("Error: Could not load configuration")
                return 1
            
            # Initialize reclass manager
            reclass_mgr = ReclassManager(
                self.config.merged_inventory_dir,
                dry_run=self.config.dry_run
            )
            
            # Apply filters if provided
            nodes = reclass_mgr.filter_nodes(
                node_filter=self.config.node_filter,
                class_filter=self.config.class_filter,
                project_filter=self.config.project_filter
            )
            if nodes:
                print(f"Available nodes ({len(nodes)}):")
                for node in nodes:
                    print(f"  {node}")
            else:
                print("No nodes found")
            return 0
        
        elif subcommand == "show":
            if len(args) < 2:
                print("Error: nodes show requires node name")
                return 1
            
            node_name = args[1]
            reclass_mgr = ReclassManager(
                self.config.merged_inventory_dir,
                dry_run=self.config.dry_run
            )
            
            node_data = reclass_mgr.get_node_data(node_name)
            if node_data:
                print(f"Node: {node_name}")
                print(f"Classes: {node_data.get('classes', [])}")
                print(f"Applications: {node_data.get('applications', [])}")
                print("Parameters:")
                for key, value in node_data.get('parameters', {}).items():
                    print(f"  {key}: {value}")
            else:
                print(f"Node not found: {node_name}")
                return 1
            return 0
        else:
            print(f"Error: Unknown nodes subcommand: {subcommand}")
            return 1
    
    def cmd_ansible(self, args: list[str]) -> int:
        """Ansible integration commands."""
        if not args:
            print("Error: ansible command requires module name")
            return 1
        
        self.load_config()
        if not self.config:
            print("Error: Could not load configuration")
            return 1
        
        from ..core.ansible import AnsibleManager
        ansible_mgr = AnsibleManager(self.config)
        
        if args[0] == "playbook":
            if len(args) < 2:
                print("Error: ansible playbook requires playbook path")
                return 1
            
            playbook_path = Path(args[1])
            extra_args = args[2:] if len(args) > 2 else []
            
            # Parse additional options
            extra_vars = {}
            become = False
            hosts = None
            
            i = 0
            while i < len(extra_args):
                arg = extra_args[i]
                if arg == "--become":
                    become = True
                elif arg == "-l" or arg == "--limit":
                    if i + 1 < len(extra_args):
                        hosts = extra_args[i + 1]
                        i += 1
                elif arg.startswith("-e") or arg == "--extra-vars":
                    if i + 1 < len(extra_args):
                        var_pair = extra_args[i + 1]
                        if "=" in var_pair:
                            key, value = var_pair.split("=", 1)
                            extra_vars[key] = value
                        i += 1
                i += 1
            
            success = ansible_mgr.execute_playbook(
                playbook_path,
                hosts=hosts,
                extra_vars=extra_vars,
                become=become
            )
            return 0 if success else 1
        
        else:
            # Execute module
            module = args[0]
            module_args = " ".join(args[1:]) if len(args) > 1 else None
            
            success = ansible_mgr.execute_module(module, module_args)
            return 0 if success else 1
    
    def cmd_status(self, args: list[str]) -> int:
        """Check host connectivity."""
        self.load_config()
        if not self.config:
            print("Error: Could not load configuration")
            return 1
        
        from ..core.ansible import AnsibleManager
        ansible_mgr = AnsibleManager(self.config)
        
        print("Checking host connectivity...")
        success = ansible_mgr.ping_hosts()
        
        if success:
            print("Host connectivity check completed")
            return 0
        else:
            print("Host connectivity check failed")
            return 1
    
    def cmd_merge(self, args: list[str]) -> int:
        """Merge storage directories."""
        self.load_config()
        print("Merging storage directories...")
        print("  (Merge functionality not yet implemented)")
        return 0
    
    def cmd_search(self, args: list[str]) -> int:
        """Search inventory and playbooks."""
        if not args:
            print("Error: search command requires pattern")
            return 1
        
        pattern = args[0]
        self.load_config()
        print(f"Searching for pattern: {pattern}")
        print("  (Search functionality not yet implemented)")
        return 0
    
    def cmd_migrate(self, args: list[str]) -> int:
        """Migration utilities."""
        if not args or args[0] != "--from-bash":
            print("Error: migrate command requires --from-bash option")
            return 1
        
        if len(args) < 2:
            bash_config_path = Path(".maestro")
        else:
            bash_config_path = Path(args[1])
        
        if not bash_config_path.exists():
            print(f"Error: Bash config file not found: {bash_config_path}")
            return 1
        
        print(f"Migrating from bash config: {bash_config_path}")
        config = self.config_manager.migrate_from_bash(bash_config_path)
        
        # Save migrated config
        new_config_path = Path.cwd() / "pyestro.json"
        self.config_manager.save_config(config, new_config_path)
        
        print(f"Migration completed. New config saved to: {new_config_path}")
        return 0
    
    def cmd_git(self, args: list[str]) -> int:
        """Git operations."""
        if not args:
            print("Error: git command requires subcommand (init, status, pull)")
            return 1
        
        subcommand = args[0]
        self.load_config()
        if not self.config:
            print("Error: Could not load configuration")
            return 1
        
        from ..core.git import GitManager
        git_mgr = GitManager(self.config.dry_run)
        
        if subcommand == "init":
            # Clone all configured repositories
            repo_configs = self.config.get_repository_configs()
            print(f"Initializing {len(repo_configs)} repositories...")
            
            results = git_mgr.clone_repositories(repo_configs, self.config.maestro_dir)
            
            for repo_name, result in results.items():
                if result["success"]:
                    print(f"  ✓ {repo_name}")
                else:
                    print(f"  ✗ {repo_name} (failed)")
            
            return 0
        
        elif subcommand == "status":
            # Show status of all repositories
            print("Repository status:")
            repo_configs = self.config.get_repository_configs()
            
            for repo_config in repo_configs:
                repo_dir = self.config.maestro_dir / repo_config.name
                status = git_mgr.get_repository_status(repo_dir)
                
                if status:
                    changes_str = " (uncommitted changes)" if status["has_changes"] else ""
                    print(f"  {repo_config.name}: {status['branch']} ({status['commit']}){changes_str}")
                else:
                    print(f"  {repo_config.name}: not found or not a git repository")
            
            return 0
        
        elif subcommand == "pull":
            # Pull all repositories
            repo_configs = self.config.get_repository_configs()
            print(f"Pulling updates for {len(repo_configs)} repositories...")
            
            for repo_config in repo_configs:
                repo_dir = self.config.maestro_dir / repo_config.name
                success = git_mgr.pull_repository(repo_dir)
                print(f"  {'✓' if success else '✗'} {repo_config.name}")
            
            return 0
        
        else:
            print(f"Error: Unknown git subcommand: {subcommand}")
            return 1
    
    def cmd_setup(self, args: list[str]) -> int:
        """Setup project dependencies and repositories."""
        self.load_config()
        if not self.config:
            print("Error: Could not load configuration")
            return 1
        
        print("Setting up Pyestro project...")
        
        # Clone repositories
        print("\n1. Cloning repositories...")
        git_mgr = GitManager(dry_run=self.config.dry_run)
        repo_configs = self.config.get_repository_configs()
        
        if repo_configs:
            results = git_mgr.clone_repositories(repo_configs, self.config.maestro_dir)
            for repo_name, result in results.items():
                if result['success']:
                    print(f"  ✓ {repo_name}")
                else:
                    print(f"  ✗ {repo_name} (failed)")
        else:
            print("  No repositories configured")
        
        # Setup directory structure
        print("\n2. Setting up directories...")
        file_mgr = FileManager(dry_run=self.config.dry_run)
        
        directories = [
            self.config.work_dir,
            self.config.merged_inventory_dir,
            self.config.maestro_dir / self.config.ansible.galaxy_roles_dir
        ]
        
        for directory in directories:
            if file_mgr.ensure_directory(directory):
                print(f"  ✓ {directory}")
            else:
                print(f"  ✗ {directory} (failed)")
        
        # Create ansible.cfg
        print("\n3. Setting up Ansible configuration...")
        try:
            ansible_mgr = AnsibleManager(self.config)
            if ansible_mgr.create_ansible_cfg():
                print("  ✓ ansible.cfg created")
            else:
                print("  ✗ ansible.cfg creation failed")
        except Exception as e:
            print(f"  ✗ Ansible setup failed: {e}")
        
        # Merge inventory directories
        print("\n4. Merging inventory directories...")
        if self.config.inventory_dirs:
            source_dirs = []
            for name, path in self.config.inventory_dirs.items():
                if path and path != "none":
                    source_path = Path(path)
                    if source_path.exists():
                        source_dirs.append(source_path)
            
            if source_dirs:
                if file_mgr.merge_directories(source_dirs, self.config.merged_inventory_dir):
                    print(f"  ✓ Merged {len(source_dirs)} inventory directories")
                else:
                    print("  ✗ Inventory merge failed")
            else:
                print("  No inventory directories found")
        else:
            print("  No inventory directories configured")
        
        # Check dependencies
        print("\n5. Checking dependencies...")
        dependencies = {
            "git": GitManager(dry_run=True)._find_git(),
            "reclass": ReclassManager(self.config.merged_inventory_dir, dry_run=True)._find_reclass(),
            "ansible": AnsibleManager(self.config)._find_ansible(),
            "ansible-playbook": AnsibleManager(self.config)._find_ansible_playbook(),
            "rsync": FileManager(dry_run=True)._find_rsync()
        }
        
        for dep_name, dep_path in dependencies.items():
            if dep_path:
                print(f"  ✓ {dep_name}: {dep_path}")
            else:
                print(f"  ✗ {dep_name}: not found")
        
        missing_deps = [name for name, path in dependencies.items() if not path]
        if missing_deps:
            print(f"\nMissing dependencies: {', '.join(missing_deps)}")
            print("Please install them using your system package manager.")
            print("For example:")
            if "reclass" in missing_deps:
                print("  pip install reclass")
            if "ansible" in missing_deps:
                print("  pip install ansible")
            if "git" in missing_deps:
                print("  # Install Git using your package manager")
            if "rsync" in missing_deps:
                print("  # Install rsync using your package manager")
        
        print("\nSetup completed!")
        return 0
    
    def cmd_create(self, args: list[str]) -> int:
        """Create new project from template."""
        if not args:
            print("Error: create command requires arguments")
            print("Usage: pyestro create <template> <name> [options]")
            print("       pyestro create --wizard")
            print("       pyestro create --list")
            return 1
        
        # Initialize project generator
        generator = ProjectGenerator()
        
        # Handle special options
        if args[0] == "--list":
            templates = generator.list_templates()
            if not templates:
                print("No templates available!")
                return 1
            
            print("Available project templates:")
            for template in templates:
                description = template.get('description', 'No description')
                print(f"  {template['name']:<15} - {description}")
            return 0
        
        elif args[0] == "--wizard":
            return 0 if generator.interactive_create() else 1
        
        else:
            # Standard create command: pyestro create <template> <name>
            if len(args) < 2:
                print("Error: create command requires template name and project name")
                print("Usage: pyestro create <template> <name>")
                print("       pyestro create --list  (to see available templates)")
                return 1
            
            template_name = args[0]
            project_name = args[1]
            
            # Parse additional options
            target_dir = None
            variables = {}
            
            i = 2
            while i < len(args):
                arg = args[i]
                if arg == "--dir" and i + 1 < len(args):
                    target_dir = Path(args[i + 1])
                    i += 2
                elif arg.startswith("--var="):
                    # Handle --var=key=value
                    var_part = arg[6:]  # Remove --var=
                    if "=" in var_part:
                        key, value = var_part.split("=", 1)
                        variables[key] = value
                    i += 1
                else:
                    print(f"Unknown option: {arg}")
                    return 1
            
            # Set default target directory
            if target_dir is None:
                target_dir = Path.cwd() / project_name
            
            # Create the project
            print(f"Creating project '{project_name}' using template '{template_name}'...")
            success = generator.create_project(
                template_name, 
                project_name, 
                target_dir, 
                variables,
                dry_run=self.dry_run
            )
            
            if success:
                print(f"Project created successfully in: {target_dir}")
                print("\nNext steps:")
                print(f"  cd {target_dir}")
                print("  # Edit pyestro.json to configure your setup")
                print("  pyestro config validate")
                return 0
            else:
                print("Failed to create project!")
                return 1
    
    def run(self, args: list[str]) -> int:
        """Run CLI with given arguments."""
        command, command_args = self.parse_args(args)
        
        if command == "help":
            print_usage()
            return 0
        elif command == "version":
            print_version()
            return 0
        elif command == "create":
            return self.cmd_create(command_args)
        elif command == "setup":
            return self.cmd_setup(command_args)
        elif command == "init":
            return self.cmd_init(command_args)
        elif command == "config":
            return self.cmd_config(command_args)
        elif command == "nodes":
            return self.cmd_nodes(command_args)
        elif command == "ansible":
            return self.cmd_ansible(command_args)
        elif command == "status":
            return self.cmd_status(command_args)
        elif command == "merge":
            return self.cmd_merge(command_args)
        elif command == "search":
            return self.cmd_search(command_args)
        elif command == "migrate":
            return self.cmd_migrate(command_args)
        elif command == "git":
            return self.cmd_git(command_args)
        elif command == "setup":
            return self.cmd_setup(command_args)
        else:
            print(f"Error: Unknown command: {command}")
            print_usage()
            return 1


def cli() -> None:
    """Main CLI entry point."""
    cli_handler = CLI()
    exit_code = cli_handler.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
