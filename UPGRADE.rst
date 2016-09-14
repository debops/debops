.. _apt__ref_upgrade_nodes:

Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
:ref:`apt__ref_changelog` for more details about what has changed.

From v0.2.0 to v0.3.0
---------------------

The APT proxy configuration is moved to a separate role, ``debops.apt_proxy``.
Consult its documentation to see how to configure it. The current proxy
configuration is left in place on existing systems, you might consider removing
it when new role creates its own configuration file.

The ``apt-listchanges`` package is managed using ``debops.apt_listchanges``
role. The ``apticron`` package is currently not installed by default (it is not
removed on existing systems).
