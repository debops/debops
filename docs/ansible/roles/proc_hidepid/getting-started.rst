Getting started
===============

.. contents::
   :local:


Static GID assignment
---------------------

The ``procadmins`` group uses a static GID ``70``, chosen based on the default
set of system groups provided in Debian with usable range between 61-99. This
becomes important in environments with LXC containers where, depending on the
configuration, host and container GIDs could differ, resulting in a different
set of users being able to see the :file:`/proc` contents. Thus, the need to
synchronize the GID between distinct environments sharing the same GID
namespace (the same kernel).


Ansible local facts
-------------------

The ``debops.proc_hidepid`` role provides a set of Ansible local facts
available in the ``ansible_local.proc_hidepid.*`` hierarchy. You can use the
facts to add application UNIX accounts to the correct UNIX system group that
allows them access to the ``/proc`` filesystem.


Example inventory
-----------------

The ``debops.proc_hidepid`` role is included by default in the ``common.yml``
DebOps playbook; you don't need to add hosts to any Ansible groups to enable
it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.proc_hidepid`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/proc_hidepid.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::proc_hidepid``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
