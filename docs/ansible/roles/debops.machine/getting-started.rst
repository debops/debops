Getting started
===============

.. contents::
   :local:

Default configuration
---------------------

By default, the role will remove an existing :file:`/etc/motd` file to move the
original Debian/Ubuntu MOTD out of the way. This can be controlled using the
:envvar:`machine__etc_motd_state` variable. The original version of the file is
maintained by the ``base-files`` package and can be found in the
:file:`/usr/share/base-files/motd` file.

You can use the :file:`/etc/motd.tail` file to include manual text in the
dynamic MOTD. Alternatively, you can put a custom script in the
:file:`/etc/update-motd.d/` directory.

You can use the :ref:`debops.resources` Ansible role to install multiple custom
scripts in the :file:`/etc/update-motd.d/` directory at once by copying them
from the :file:`resources/` subdirectory on the Ansible Controller.


Ansible local facts
-------------------

The ``debops.machine`` role provides a set of Ansible local facts available in
the ``ansible_local.machine.*`` hierarchy. They will contain contents of the
:file:`/etc/machine-info` variables, so that they could be used by other
Ansible roles when configured.


Example inventory
-----------------

The ``debops.machine`` role is included by default in the ``common.yml`` DebOps
playbook; you don't need to add hosts to any Ansible groups to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.machine`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/machine.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::machine``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
