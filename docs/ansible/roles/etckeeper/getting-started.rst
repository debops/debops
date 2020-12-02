.. Copyright (C) 2016-2018 Robin Schneider <ypid@riseup.net>
.. Copyright (C)      2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Initial configuration
---------------------

By default :command:`git` is used as VCS. This can be changed via the
:envvar:`etckeeper__vcs` variable through Ansible inventory.

The role is designed with :command:`etckeeper` being already installed on
a host in mind. This can be done for example via Debian Preseeding or LXC
template installing and pre-configuring :command:`etckeeper`; the role will
keep the already existing configuration without any changes if the variables
are not overwritten through the Ansible inventory. Any changes in the
:file:`/etc/` directory will be automatically committed by Ansible local facts
before Ansible role execution.


Example inventory
-----------------

The ``debops.etckeeper`` role is part of the default DebOps playbook and run on
all hosts which are part of the ``[debops_all_hosts]`` group. To use this role
with DebOps it's therefore enough to add your host to the mentioned host group
(which most likely it is already):

.. code-block:: none

   [debops_all_hosts]
   hostname


Example playbook
----------------

Here's an example playbook that uses the ``debops.etckeeper`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/etckeeper.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::etckeeper``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
