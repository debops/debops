Getting started
===============

After DebOps scripts are installed, you need to download playbooks and roles
provided with the project. To do that, you need to run command::

    debops-update

This script will download playbooks and roles from their GitHub repositories
into your user directory. Exact location is dependent upon your operating
system:

- on Linux systems, it will be ``$XDG_DATA_HOME/debops/`` which usually is
  expanded to ``~/.local/share/debops/``;

- on MacOSX systems, it will be ``~/Library/Application Support/debops``;

When all roles are downloaded and installed, you can start using DebOps by
creating a project directory. This will be a directory which contains
everything related to a specific environment - Ansible inventory, custom
playbooks, roles, templates and files. Most of the time you will run commands
from the base of that directory. You can create it by running command::

    debops-init ~/project-directory

It can be anywhere in your filesystem. DebOps is designed to be used on an
unprivileged user account on Ansible Controller, so you don't need to be
``root`` in order to use it - most of the time you can use your existing user
account.

After entering your new project directory, you can see an ``ansible/``
directory which contains files related to Ansible, mostly inventory, secret
directory, playbooks and roles. You can also notice ``.debops.cfg``
configuration file which indicates to the DebOps script that this is indeed
a project directory and contains configuration related to it.

Main Ansible inventory file is ``ansible/inventory/hosts``. You should add
hosts that you want to manage to it, just make sure that you can access them
through SSH without issues. It's a good idea to start using groups right away
to keep many hosts under control. An example inventory file::

    [group-of-hosts]
    host1
    host2

If you want, and your Ansible Control is Debian/Ubuntu based, you can manage it
using DebOps as well. You can do it by adding its hostname to Ansible inventory
with "local" connection type::

    myhostname ansible_connection=local

When all hosts you want to use are written in inventory and you checked the
connectivity, you can run main DebOps script to generate Ansible configuration
and execute default DebOps playbooks::

    debops

The ``debops`` command is a wrapper for ``ansible-playbook``, which means that you can pass any ``ansible-playbook`` parameters to it. For example, to limit the Ansible run to a specific host, you can execute command::

    debops --limit host1

