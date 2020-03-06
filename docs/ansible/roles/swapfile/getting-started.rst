.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _swapfile__ref_getting_started:

Getting started
===============

.. only:: html

   .. contents::
      :local:

Example inventory
-----------------

To enable swap files on a host, it needs to be added to the
``[debops_service_swapfile]`` group in Ansible’s inventory::

    [debops_service_swapfile]
    hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.swapfile`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/swapfile.yml
   :language: yaml
   :lines: 1,6-
