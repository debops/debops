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


.. _apt_signing_key_not_bound:

"Signing key is not bound" error
--------------------------------

SHA1 algorithm used in old GPG signatures is considered not secure after
2026-02-01. This can cause an error message during APT update and can result in
an error during Ansible execution. Fixing this issue requires updated APT
repository keys that can only be done by third parties.

There are two ways to mitigate the issue in the meantime, described in `an
Ansible forum post`__. First one is to override the default APT Sequoia
configuration stored in :file:`/usr/share/apt/default-sequoia.config`
configuration file to change the cutoff date for specific signature algorithms.
This method is not implemented in DebOps at the moment.

The other way is to mark specific APT repositories as trusted, using
``[trusted=yes]`` option in APT repository configuration. This way is more
granular and visible to the system administrator, therefore it will be used in
APT repositories managed by DebOps when needed.

.. __: https://forum.ansible.com/t/ubuntu-ppa-key-signature/45237


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
