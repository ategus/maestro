# Documentation Setup for Pyestro

## Recommended: MkDocs with Material Theme

### Installation
```bash
pip install mkdocs mkdocs-material
```

### Quick Setup
```bash
cd /Users/rox/code/test/maestro/pyestro
mkdocs new docs
cd docs
```

### Configuration (mkdocs.yml)
```yaml
site_name: Pyestro Documentation
site_description: Python Configuration Management Orchestrator
site_author: Your Name

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.highlight
    - search.share
    - content.code.annotate

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
    - Configuration: getting-started/configuration.md
  - User Guide:
    - Commands: user-guide/commands.md
    - Reclass Integration: user-guide/reclass.md
    - Ansible Integration: user-guide/ansible.md
  - Developer Guide:
    - Architecture: developer-guide/architecture.md
    - API Reference: developer-guide/api.md
    - Contributing: developer-guide/contributing.md
  - Reference:
    - Configuration Schema: reference/config-schema.md
    - CLI Reference: reference/cli.md
    - Migration Guide: reference/migration.md

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - admonition
  - pymdownx.arithmatex:
      generic: true
  - footnotes
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.mark
  - attr_list
  - md_in_html

plugins:
  - search
  - autorefs

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/yourname/pyestro
```

### Commands
```bash
# Serve locally
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Alternative: Simple Static Site

### For minimal setup, use **Docsify**:
```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Pyestro Documentation</title>
  <meta name="description" content="Python Configuration Management Orchestrator">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css">
</head>
<body>
  <div id="app"></div>
  <script>
    window.$docsify = {
      name: 'Pyestro',
      repo: 'https://github.com/yourname/pyestro',
      loadSidebar: true,
      coverpage: true,
      onlyCover: false,
      search: 'auto',
      subMaxLevel: 2,
      auto2top: true
    }
  </script>
  <script src="//cdn.jsdelivr.net/npm/docsify@4"></script>
  <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-bash.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/prismjs@1/components/prism-python.min.js"></script>
</body>
</html>
```

## Comparison

| Framework | Complexity | Build Step | Themes | Features | Best For |
|-----------|------------|------------|---------|----------|----------|
| MkDocs | Low | Yes | Excellent | Search, Nav | Python projects |
| Docusaurus | Medium | Yes | Great | Versioning, Blog | Large projects |
| Docsify | Very Low | No | Good | Minimal setup | Simple docs |
| GitBook | Low | No | Excellent | Collaboration | Team docs |
| VuePress | Medium | Yes | Good | Vue integration | Vue projects |

## Recommendation for Pyestro

**Go with MkDocs + Material theme** because:
- ✅ Perfect for Python projects
- ✅ Beautiful, professional appearance
- ✅ Easy to setup and maintain
- ✅ Great search functionality
- ✅ Responsive design
- ✅ Can be deployed to GitHub Pages easily
- ✅ Supports code highlighting for Python/Bash
- ✅ Good navigation for technical docs
