Custom DebOps features
======================

To make integration of DebOps roles with your own infrastructure easier, DebOps
playbooks include a set of Ansible plugins and introduce several new concepts
to Ansible best practices.

The project directory
---------------------

By default, Ansible is written to use ``/etc/ansible/`` directory and its
contents in daily use. In contrast to this, DebOps playbooks are designed to be
used from a custom local directory, which you can initialize using
``debops-init`` command. By using Ansible this way, it's much easier to create
multiple, separate environments with distinct inventories and configuration. To
change the environment you are working in, you just need to switch to
a different directory - there's no need to use separate Ansible host groups,
custom variables and so on.

The official playbooks and roles are installed in central, fixed location
(``~/.local/share/debops/debops-playbooks/`` on Linux systems), and the
``debops`` script generates ``ansible.cfg`` configuration file to provide
correct paths for ``ansible-playbook`` command to use them indirectly from the
project directory.

You can store your custom playbooks and roles in the project directory, in
``playbooks/`` and ``roles/`` subdirectories.

Host group namespace
--------------------

Default DebOps playbooks use the ``[debops_*]`` group namespace in Ansible
inventory (for example, ``debops.nginx`` role is activated on hosts in
``[debops_nginx]`` group). This lets you design your own inventory layout with
groups and parent groups as you with, without worrying that you might clash
with DebOps host groups. You can also define inventory variables for a specific
DebOps role using its group name.

Flattened lists in inventory
----------------------------

Some DebOps roles use sets of default variables (usually lists) to allow you to
define different settings for all hosts in inventory, a group of hosts, or even
specific hosts. For example, using ``debops.sshd`` role you can whitelist
a certain subnet for all hosts in your inventory, add another subnet for
a pariticular group of hosts, and so on. You can also override more general
list on specific hosts if needed.

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

By combining above techniques, you can very eaily extend DebOps roles without
losing the ability to update them using ``git`` without merge conflicts.

LDAP integration
----------------

Certain DebOps roles can access LDAP server to create or update data as needed.
Custom modules are provided for LDAP entry and attribute management, deeper
integration is planned in the future.

