.. Copyright (C) 2016-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Example inventory
-----------------

The ``debops.logrotate`` role is included in the :file:`common.yml` DebOps
playbook, so you don't need to enable it separately.

Example playbook
----------------

Here's an example playbook which uses ``debops.logrotate`` role::

    ---

    - name: Configure log rotation
      hosts: [ 'debops_all_hosts', 'debops_service_logrotate' ]
      become: True

      roles:

        - role: debops.logrotate
          tags: [ 'role::logrotate' ]

