Getting started
===============

.. contents::
   :local:


.. _system_groups__ref_acl:

Access Control List
-------------------

The ``debops.system_groups`` role maintains a simple Access Control List in the
Ansible local facts, under ``ansible_local.system_groups.access.*`` variable
hierarchy. Other roles can inspect it to get a list of UNIX group names which
they can use to configure access in their respective applications.

The ``ansible_local.system_groups.access`` variable is a YAML dictionary. Each
key of this dictionary corresponds to a particular resource, and the value is
a list of UNIX group names. The resources are user-defined, by default the role
creates:

``root``
  Members of these UNIX groups have full, privileged access to the ``root``
  account on a given host. This resource should be reserved to system
  administrators.

``sshd``
  Members of these UNIX groups can login to the host via the SSH service.
  See :ref:`debops.sshd` role for more details.

``webserver``
  Members of these UNIX groups can manipulate various webserver-related
  services. See :ref:`debops.nginx` and :ref:`debops.php` roles for more
  details.


Example inventory
-----------------

The ``debops.system_groups`` role is included by default in the ``common.yml``
DebOps playbook; you don't need to add hosts to any Ansible groups to enable
it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.system_groups`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/system_groups.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::system_groups``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.system_groups`` Ansible
role:

- Manual pages: :man:`group(5)`, :man:`sudoers(5)`, :man:`tmpfiles.d(5)`
- `Debian System Groups`__ documentation on Debian Wiki
- `UNIX permissions`__ documentation on Debian Wiki
- `User Private Groups`__ documentation on Debian Wiki
- `Security privileges`__ documentation on Ubuntu Wiki
- `Multi User Management`__ documentation on Ubuntu Wiki
- `UNIX group identifier`__ page on Wikipedia

.. __: https://wiki.debian.org/SystemGroups
.. __: https://wiki.debian.org/Permissions
.. __: https://wiki.debian.org/UserPrivateGroups
.. __: https://wiki.ubuntu.com/Security/Privileges
.. __: https://wiki.ubuntu.com/MultiUserManagement
.. __: https://en.wikipedia.org/wiki/Group_identifier
