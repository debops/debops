DebOps for Ansible users
========================

This document explains certain aspects of the DebOps project to existing
Ansible users.


Roles and playbooks are read-only
---------------------------------

Current Ansible ecosystem relies on Ansible Galaxy for role distribution. The
usual use case for Galaxy roles is either as examples to write your roles,
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
roles when writing custom ones by users. For example, when you write a role that
deploys a web application, you don't need to worry about required
:ref:`firewall configuration <debops.ferm>`, :ref:`web server <debops.nginx>`
or :ref:`system package upgrades <debops.unattended_upgrades>`; existing roles
can handle that for you.


Roles and playbooks are shared between multiple inventories
-----------------------------------------------------------

The custom :command:`debops*` scripts provided with DebOps support creation and
management of multiple "project directories". Each project directory contains
its own Ansible inventory, as well as custom playbooks, roles and other
resources written for that environment. This allows easy creation of
development, test and production environments that use the same set of
playbooks and differ only via inventory variables.


Ansible inventory is a source of truth
--------------------------------------

DebOps roles don't modify the Ansible inventory directly, it is treated as the
"source of truth" defined by the user. This means that users can provide any
inventory they want to use, be it a set of static YAML files, or a dynamic
inventory based on scripts and a database. Users don't even need to
specifically configure things, many roles use sensible defaults to configure
the host according to its environment (DNS domain name, IP addresses, number of
CPU cores, amount of RAM, network interfaces, etc.). The aim is to have roles
that work fine with the default configuration in a typical Debian installation,
with configuration tweaked to provide more security when necessary.
