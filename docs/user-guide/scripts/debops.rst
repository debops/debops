.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _cmd_debops:

The :command:`debops` command
=============================

Wraps :command:`ansible-playbook` and since that's the most commonly ran command we
decided it's a good idea to shorten it to ``debops`` instead of ``debops-playbook``.

Any arguments that :command:`ansible-playbook` supports can be passed to ``debops``.

You don't need to specify an inventory or playbook. Part of the benefit of
using this tool is that it figures out all of that stuff for you. You can still
chain together multiple playbooks, custom or not.

Example commands:

.. code:: shell

    debops -l mygroup

    debops -t foo
