.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _cmd_debops-defaults:

The :command:`debops-defaults` command
======================================

Collect the default values of all DebOps roles and output them as
one output stream.

By default the output will be displayed using `view`.

Example commands:

.. code:: shell

    debops-defaults

    debops-defaults | less

    debops-defaults > defaults.txt

    debops-defaults mysql postgresql nginx
