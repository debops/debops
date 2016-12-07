The ``debops-update`` command
=============================

Updates the playbooks and roles relative to ``$PWD``, if none are found
then it will update them at their default location.

When passing the ``--dry-run`` argument, ``debops-update`` will just print
a summary of the actions that would be performed without actually executing
them.
This is useful to further inspect what and which role the update will change,
in order to adapt, if necessary, the local inventory and variables before applying
it.

Example commands:

.. code:: shell

    debops-update ~/my-debops-roles-dir

    debops-update --dry-run
