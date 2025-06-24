# Installation

## Prerequisites

- **Python 3.8+** - Pyestro requires Python 3.8 or later
- **Git** - For repository management
- **Optional**: reclass, Ansible (for full functionality)

## Installation Methods

### From Source

```bash
# Clone the repository
git clone https://github.com/yourname/pyestro.git
cd pyestro

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Using pip (when available)

```bash
pip install pyestro
```

## Verify Installation

```bash
# Check if Pyestro is working
python pyestro.py --version

# Run basic status check
python pyestro.py status
```

## Optional Dependencies

### Reclass

For full inventory management functionality:

```bash
pip install reclass
```

### Ansible

For configuration management features:

```bash
pip install ansible
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Configuration Setup](configuration.md)
