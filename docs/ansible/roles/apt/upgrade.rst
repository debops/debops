.. _apt__ref_upgrade_notes:

Upgrade notes
=============

.. include:: ../../../includes/global.rst

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
changelog for more details about what has changed.


From v0.3.0 to v0.4.0
---------------------

Make sure to read the Changelog for all of the important changes. Some
variables were renamed or removed, you might need to update your inventory.
For this you might find the following script useful which can rename a subset
of the changed variables in your inventory:

.. literalinclude:: scripts/upgrade-from-v0.3.x-to-v0.4.x
   :language: shell

The script is bundled with this role under
:file:`./docs/scripts/upgrade-from-v0.3.x-to-v0.4.x` and can be invoked from
their. Note that not all variable names can be updated automatically.

The method of configuring "delayed repositories" has been changed from
a separate variable lists to using the ``state`` parameter and local facts.
Refer to :ref:`apt__ref_defaults_detailed`.

The order of the APT sources in the :file:`/etc/apt/sources.list` file has been changed;
first the sources from Ansible inventory (if any) are configured, then the
original sources (if detected), then the default mirrors, and security sources
afterwards. This seems to be the preferred ordering of the entries, which
allows downloading of the packages from the closes sources if available. The
order can be configured using the ``apt__combined_sources`` list.


From v0.2.0 to v0.3.0
---------------------

The APT proxy configuration has been moved to debops.apt_proxy_.
Consult its documentation to see how to configure it.
The current proxy configuration (:file:`/etc/apt/apt.conf.d/000apt-cacher-ng-proxy`)
is left in place on existing systems.
You might consider removing it when another role (like debops.apt_proxy_)
manages the APT proxy configuration. The file can be removed using the
debops.resources_ role and the following snippet in your inventory:

.. code-block:: yaml

   resources__files:

     - path: '/etc/apt/apt.conf.d/000apt-cacher-ng-proxy'
       state: 'absent'

Note that debops.apt_proxy_ will pick up proxy servers specified via the
debops.environment_ role. In case you run a separate proxy server for APT (as
configurable by debops.apt_cacher_ng_) you might prefer the behavior of v0.2.0
where the APT proxy was specified separately.

In that case you might find the following script useful which can update your
inventory accordingly:

.. literalinclude:: scripts/upgrade-proxy-from-v0.2.x-to-v0.3.x
   :language: shell

The script is bundled with this role under
:file:`./docs/scripts/upgrade-proxy-from-v0.2.x-to-v0.3.x` and can be invoked from
their.

The :command:`apt-listchanges` package is managed using debops.apt_listchanges_
role. The ``apticron`` package is currently not installed by default (it is not
removed on existing systems).
