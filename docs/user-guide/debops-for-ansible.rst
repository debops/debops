.. _debops_for_ansible:

DebOps for Ansible users
========================

.. include:: ../includes/global.rst

To make integration of DebOps roles with your own infrastructure easier,
DebOps playbooks introduce several new concepts to Ansible best practices.


Roles and playbooks are read-only
---------------------------------

The current Ansible ecosystem relies on Ansible Galaxy for role distribution.
The usual use case for Galaxy roles is either as examples to write your roles,
or to heavily modify them according to your own needs.

DebOps roles and provided playbooks are designed to be used in a "read-only"
mode. This allows easy upgrades of the project codebase by using the
:command:`git pull` command, as well as distributed development model where
changes and new features can be shared between DebOps users through the central
repository. You are not expected to have to modify roles directly; any and all
changes necessary should be supported by the role default variables which can
then be modified as needed through Ansible inventory.

Many roles support usage as "role dependencies" - other roles, either those in
DebOps or written by its users, can request certain configuration to be defined
on their behalf. This design principle allows for the DebOps roles to be
focused on specific services or applications and encourages re-use of existing
roles when writing custom ones by users.

For example, when you write a role that deploys a web application, you don't
need to worry about required :ref:`firewall configuration <debops.ferm>`,
:ref:`web server <debops.nginx>` or
:ref:`system package upgrades <debops.unattended_upgrades>`; existing roles
can handle that for you.


Roles and playbooks are shared between multiple inventories
-----------------------------------------------------------

The custom :command:`debops*` scripts provided with DebOps supports the creation
and management of multiple "project directories".
Each project directory contains its own Ansible inventory, as well as custom
playbooks, roles and other resources written for that environment.
This allows easy creation of development, test and production environments that
use the same set of playbooks and differ only via inventory variables.

The official playbooks and roles are installed in central, fixed location
(:file:`~/.local/share/debops/debops-playbooks/` on Linux systems), and the
``debops`` script generates ``ansible.cfg`` configuration file to provide
correct paths for the :command:`ansible-playbook` command to use them indirectly
from the project directory.


The common playbook
-------------------

In many Ansible environments a popular practice is to have a "common role" that
contains tasks that are expected to be run on any and all hosts managed by
Ansible.

In DebOps, there is an entire playbook dedicated to this, located in
:file:`playbooks/common.yml`. It includes multiple roles that prepare a host
from an unknown to a known state - for example, a :program:`ferm`-based firewall
will be installed and configured on a given host, unless disabled, some common,
useful packages will be installed, and so on.

Other DebOps roles not included in the :file:`common.yml` playbook are designed
for hosts that were configured by it - they might work outside of that
environment, but it's not guaranteed.


File, template and task hooks
-----------------------------

DebOps project introduces a set of Ansible lookup plugins which allow you to
override certain aspects of public Ansible roles without modifying them
directly. This allows for easier updates or customization of the files and
templates according to your specific needs.

Certain roles use ``file_src`` or ``template_src`` to calculate path to files
or templates used by a role. You can override these paths using ``.debops.cfg``
configuration file and provide your own versions of files and templates stored
in DebOps project directory.

Some roles provide "task hooks" at the beginning and end of task lists, which
are empty files in a specific subdirectories. Using ``task_src`` lookup plugin
and settings defined in ``.debops.cfg`` configuration file you can "inject"
your own tasks at the beginning or end of these roles, which gives you more
control over the configuration.

By combining above techniques, you can very easily extend DebOps roles without
losing the ability to update them, using :command:`git` without having merge
conflicts.


Ansible inventory is a source of truth
--------------------------------------

DebOps roles don't modify the Ansible inventory directly, it is treated as the
"source of truth" defined by the user. This means that users can provide any
inventory they want to use, be it a set of static YAML files, or a dynamic
inventory based on scripts and a database.

Users don't even need to specifically configure things, as many roles use
sensible defaults to configure the host according to its environment
(DNS domain name, IP addresses, number of CPU cores, amount of RAM,
network interfaces, etc.).

The aim is to have roles that work fine with the default configuration in a
typical Debian installation, automatically implementing best practices for
security where necessary.


Flattened lists in inventory
----------------------------

Some DebOps roles use sets of default variables (usually lists) to allow you to
define different settings for all hosts in inventory, a group of hosts, or even
specific hosts.

For example, using the ``debops.sshd`` role you can whitelist a certain subnet
for all hosts in your inventory, add another subnet for a particular group of
hosts, and so on.

You can also override the more general list on specific hosts if needed.


The ``[debops_*]`` host group namespace
---------------------------------------

To make host configuration in Ansible inventory more explicit, DebOps uses
a set of Ansible host groups. All of the official groups are set in the
``[debops_*]`` namespace, so you are free to use other names without any
possibility of a collision.

Common DebOps playbook, as well as some other service playbooks that are
included in it, use ``[debops_all_hosts]`` group. This is a base group of the
project and all hosts managed by DebOps should be included in it.

Service playbooks use the ``[debops_service_*]`` group namespace in Ansible
inventory (for example, the ``debops.nginx`` role is activated on hosts in
``[debops_service_nginx]`` group). Some service playbooks use additional groups
for various purposes; you are advised to check the role documentation to see
what is their intended use case.


LDAP integration
----------------

Certain DebOps roles can access LDAP server to create or update data as needed.
Custom modules are provided for LDAP entry and attribute management, deeper
integration is planned in the future.
