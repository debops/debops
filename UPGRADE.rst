.. _users__ref_upgrade_nodes:

Upgrade notes
=============

.. include:: includes/all.rst

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
:ref:`users__ref_changelog` for more details about what has changed.


From v0.1.6 to v0.2.0
---------------------

All role variables have been renamed from ``users_*`` to ``users__*`` to move
them to a separate namespace. Old user account and group lists still are
supported, however you might need to update some variables like
``users_enabled`` and ``users_default_*`` to the new names in the inventory to
keep their functionality.
