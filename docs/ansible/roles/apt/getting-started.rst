.. Copyright (C) 2013-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Default configuration
---------------------

The ``non-free`` and ``non-free-firmware`` sections of the Debian Archive will
be enabled automatically on hardware-based hosts in case any non-free firmware
is required. Otherwise, only the ``main`` and ``universe`` (on Ubuntu)
repositories are enabled. Users can control this using the
:envvar:`apt__nonfree` and :envvar:`apt__nonfree_firmware` boolean variables.


Example inventory
-----------------

The ``debops.apt`` role is included by default in the :file:`layer/common.yml`
DebOps playbook; you don't need to do anything to have it executed.

If you don’t want to let ``debops.apt`` manage APT, you can do this with the
following setting in your inventory:

.. code-block:: yaml

   apt__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apt`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/apt.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::apt``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::apt:keys``
  Deploy only keys defined in inventory. Useful, if some keys are expired and
  the apt role refuses to work. Or start using debops on existing hosts with
  expired keys.
