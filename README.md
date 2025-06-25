# Maestro README #
Orchestrate a number of different orchestras (i.e. config management environements).

![Maestro Logo](maestro.png "A thumbsketch of what this is all about..")

## 🚀 New: Pyestro - Python Successor

**Maestro has been modernized as [Pyestro](./pyestro/)!** Pyestro is a complete rewrite in Python that provides:

- Modern Python architecture with type hints and comprehensive testing
- Enhanced security and validation features
- Improved configuration management with YAML support
- Better integration with modern DevOps workflows
- Comprehensive documentation and tutorials

For new projects, we recommend using **Pyestro**. See the [Pyestro Summary](./PYESTRO-SUMMARY.md) for key information, or explore the full [Pyestro Documentation](./pyestro/docs/).

---

## Introduction

'Pet' vs. 'herd'? This is the 'stable' approach!

We started with cfengine to automate our server landscape,
we even configured and administrated a mesh network based on
embedded boxes based on linux/ulibc-busybox and cfengine
at the time it was the only automation solution
out there.

Today we have several customers with different configuration
management systems already in use. There is ansible, salt, and
even some homebrew solution, we currently use in different
projects on different customer sites and we also have debops
and cfengine for our servers in place. So we started to read
about reclass..

The central idea behind maestro is to build a knowledge
base (CMDB) that can be used by several configuration management
tools. It must be flexible enough to be split up as needed
and simple enough such that one can work on several projects
without having to think too much.

## Installation

Just download the main script `./maestro.sh`,
create a project directory with a copy of the config
file `./.maestro.example` (remove '.example') in it.
Then edit the config to your needs and execute the
script to download and organize the rest of the project.

Note: The script will also clone the maestro.git repo if
it is missing. In case you start from a cloned repo, you
can also just softlink the repo inside the projects
folder and it will not be fetched again.

## Tested

Last time the whole setup was officially tested is with
Ansible v2.14.18 (python v3.11.2) and salt-formulas/reclass/
v1.7.1.

## Background

While the meta data is stored with reclass[1], the actual work on the
hosts is done via ansible[2] playbooks, the core can be found
under common-playbooks[3], but is easily extensible. This connector
supports also simple merging of plain config files and other little
tricks..

It is currently written in bash and gawk (see [4]), but will probably
be rewritten in python[5] one day.

## Migration to Pyestro

If you're currently using Maestro and want to migrate to Pyestro:

1. **Review the [Migration Guide](./pyestro/docs/docs/reference/migration.md)** for detailed migration steps
2. **Check the [Legacy Maestro Tutorial](./pyestro/docs/docs/reference/legacy-maestro-tutorial.md)** to see equivalent configurations
3. **Start with the [Pyestro Quick Start](./pyestro/docs/docs/getting-started/quickstart.md)** for new setups

Both Maestro and Pyestro can coexist during the transition period.

--
 [1] http://reclass.pantsfullofunix.net/

 [2] https://www.ansible.com/

 [3] https://github.com/zwischenloesung/common-playbooks

 [4] https://www.gnu.org/

 [5] https://www.python.org/
