.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _cmd_debops-task:

The :command:`debops-task` command
==================================

Wraps :command:`ansible`, it can accept anything :command:`ansible` does.

**Note** After ``debops`` is run once and ``ansible.cfg`` is generated, you can
use the :command:`ansible` command directly.

You could use it to run adhoc tasks against your hosts.

Example commands:

.. code:: shell

    debops-task all -m setup

    debops-task somegroup -m shell -a "touch /tmp/foo && rm -rf /tmp/foo"
