.. _apt__ref_upgrade_nodes:

Upgrade notes
=============

.. include:: includes/all.rst

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
:ref:`apt__ref_changelog` for more details about what has changed.


From v0.3.0 to v0.4.0
---------------------

Make sure to read the Changelog for all of the important changes. Some
variables were renamed or removed, you might need to update your inventory.

The method of configuring "delayed repositories" has been changed from
a separate variable lists to using the ``state`` parameter and local facts. See
the documentation for details.

The order of the APT sources in the :file:`/etc/apt/sources.list` file is changed;
first the sources from Ansible inventory (if any) are configured, then the
original sources (if detected), then the default mirrors, and security sources
afterwards. This seems to be the preferred ordering of the entries, which
allows downloading of the packages from the closes sources if available. The
order can be configured using the :envvar:`apt__combined_sources` list.


From v0.2.0 to v0.3.0
---------------------

The APT proxy configuration is moved to a separate role, debops.apt_proxy_.
Consult its documentation to see how to configure it. The current proxy
configuration is left in place on existing systems, you might consider removing
it when new role creates its own configuration file.

The :command:`apt-listchanges` package is managed using debops.apt_listchanges_
role. The ``apticron`` package is currently not installed by default (it is not
removed on existing systems).
