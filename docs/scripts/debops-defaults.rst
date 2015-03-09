The ``debops-defaults`` command
===============================

Collect the default values of all DebOps roles and output them as
one output stream.

By default the output will be displayed using `view`.

Example commands::

    debops-defaults

    debobs-defaults | less

    debobs-defaults > defaults.txt

    debops-defaults mysql postgresql nginx

