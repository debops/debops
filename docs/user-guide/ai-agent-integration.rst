.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _ai_agent_integration:

AI Agent Integration
====================

DebOps project directories can include agent skill definitions that teach
AI coding agents how to perform common infrastructure tasks. This allows
agents to add hosts, enable services, and configure roles while respecting
DebOps conventions.


AI agent skill maintenance
--------------------------

To add or update existing agent skills for a given DebOps project, run the
:command:`debops project skills` command inside a DebOps project directory:

.. code-block:: shell

   $ cd ~/src/projects/myproject
   $ debops project skills

This creates an :file:`AGENTS.md` file (if not present) in the project root and
the :file:`.agents/skills/` directory tree:

.. code-block:: text

   AGENTS.md
   .agents/skills/
   ├── <first-skill>/
   │   └── SKILL.md
   └── <second-skill>/
       └── SKILL.md

The skills are scoped to this project directory - they do not affect
other projects or the system globally. Existing skills will be updated, changes
can be reviewed using the :command:`git` commands.


Available skills
----------------

The skills follow the `Agent Skills open standard <https://agentskills.io>`_
(``SKILL.md`` format) and are compatible with OpenCode, Claude Code,
OpenAI Codex CLI, GitHub Copilot, and other tools that support the standard.

``debops-add-host``
  Guides the agent through adding a new host to the Ansible inventory:
  determining the project layout (legacy vs. modern), editing the
  :file:`hosts` file, creating host variable files, and assigning
  service groups.

``debops-debug``
  Helps the agent diagnose playbook failures, understand Ansible
  task states, and apply recovery strategies for common issues like
  unreachable hosts, YAML syntax errors, undefined variables, and
  locked secrets.

``debops-enable-service``
  Guides the agent through enabling a DebOps service role for a host or
  group: adding the host to the appropriate :file:`[debops_service_<name>]`
  group and creating role-specific variable files.

``debops-find-documentation``
  Guides the agent to the right documentation source: role default
  variables via the monorepo, role documentation via ReadTheDocs or
  manpages, and subcommand usage via manpages or ReadTheDocs.

``debops-find-source``
  Locates the DebOps source code (monorepo, Ansible Collection, or Python
  package) so the agent can read role defaults and playbook definitions.
  Includes a read-only policy - the agent must not modify DebOps source
  files.

``debops-manage-inventory``
  Describes the full inventory model: group types (``debops_all_hosts``,
  ``debops_service_*``, ``:children``), file-based variables, the
  directory layout for legacy and modern projects, and how to inspect or
  remove inventory entries.

``debops-run-playbook``
  Covers the full playbook hierarchy (``site``, ``layer/*``, ``service/*``),
  role targeting via ``--tags``/``--skip-tags``, ad-hoc commands with
  ``debops exec``, utility playbooks (``bootstrap``, ``upgrade``,
  ``reboot``, ``tools/debug``), and playbook sets for modern projects.


Example session
---------------

The following shows a typical interaction between a user and an AI coding
agent in a DebOps project directory:

.. code-block:: text

   User: Add a new web server called "web01" to the inventory and
         enable nginx on it.

   Agent: I'll start by checking the project layout and loading the
          relevant skills.

          This project uses the legacy layout (``.debops.cfg`` found).
          I'll add the host and enable nginx.

          First, I'll add web01 to ``ansible/inventory/hosts``:

          .. code-block:: ini

             [debops_all_hosts]
             web01    ansible_host=web01.example.com

             [debops_service_nginx]
             web01

          Next, I'll create host variables:

          .. code-block:: yaml

             # ansible/inventory/host_vars/web01/nginx.yml
             nginx_flavor: 'full'
             nginx__deploy_state: 'present'

          The host is ready. Would you like me to run
          ``debops check service/nginx -l web01`` to verify
          the configuration?

   User: Yes, go ahead with check.

   Agent: Running::

           debops check service/nginx -l web01

           [output truncated - dry-run diff shows what would change]

          All looks good. No errors. Ready to apply with
          ``debops run`` when you confirm.

This example demonstrates the key patterns:

- The agent determines the project layout automatically
- Skills are loaded on-demand as the task requires them
- The agent uses ``debops check`` by default and asks for confirmation
  before any ``debops run``
- No secrets are exposed, no source files are modified


Operational safety
------------------

By default, agent skills instruct agents to run :command:`debops check`
(a dry-run that shows diffs without making changes). Agents should only
run :command:`debops run` when the user explicitly confirms. This ensures
you review changes before they are applied to your infrastructure.

LLM privacy and infrastructure security
'''''''''''''''''''''''''''''''''''''''

By default, an AI coding agent might use cloud-based large language models
(LLMs) that send prompts to external API endpoints. When working with a DebOps
project, those prompts may contain infrastructure details such as hostnames, IP
addresses, network topology, service configurations, and variable values. This
could inadvertently leak sensitive information about your infrastructure to
third-party providers.

For secure operations, consider using a local Large Language Model engine that
runs entirely on your own hardware. Many coding agents support local models
through providers like Ollama, llama.cpp, and others. Using a local model keeps
all infrastructure data within your control.
