.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _debops-cli:

DebOps CLI
==========

The DebOps project includes a set of Python scripts which provide a wrapper
around Ansible and other tools. The scripts can be used to create and maintain
"project directories" which contain Ansible inventory, any installed Ansible
Collections and other data related to a given environment. You can also execute
Ansible playbooks from DebOps or other Ansible Collections as well as your own
playbooks using simple commands against the current environment.

.. toctree::
   :maxdepth: 2

   debops
   debops-project/index
   debops-exec/index
   debops-run/index
   debops-env/index
   debops-config/index

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
