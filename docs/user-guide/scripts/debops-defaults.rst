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
