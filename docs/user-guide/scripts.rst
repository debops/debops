.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _cli:

The Command Line Interface
==========================

A set of Python scripts provide a simple way to install and update the DebOps
roles and playbooks from a central location.
The scripts can be used to create multiple DebOps project directories, which
can contain separate Ansible inventories, custom playbooks and roles.

A :command:`debops` script included in the package is used as a wrapper for the
:command:`ansible-playbook` command to facilitate easy execution of the provided
roles and playbooks in different environments.

The optional :command:`debops-padlock` script can be used to create an
encrypted directory backed by `EncFS <https://en.wikipedia.org/wiki/EncFS>`_ and
secured using a `GPG <https://gnupg.org/>`_ key to allow for secure storage of
passwords and other sensitive data.

.. toctree::
   :maxdepth: 1

   scripts/debops-update
   scripts/debops-init
   scripts/debops
   scripts/debops-defaults
   scripts/debops-padlock
   scripts/debops-task

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
