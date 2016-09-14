.. _apt__ref_upgrade_nodes:

Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
:ref:`apt__ref_changelog` for more details about what has changed.

From v0.2.0 to v0.3.0
---------------------

The variable apt__proxy_url is split into two variables to support both http
and https repositories when a proxy is used: apt__http_proxy_url and 
apt__https_proxy_url.
This script can come in handy to convert apt__proxy_url into the new variables:

.. literalinclude:: scripts/upgrade-from-v0.2.x-to-v0.3.x
   :language: shell

The script is bundled with this role under
:file:`docs/scripts/upgrade-from-v0.2.x-to-v0.3.x` and can be invoked from
there.

The ``apt-listchanges`` package is managed using ``debops.apt_listchanges``
role. The ``apticron`` package is currently not installed by default (it is not
removed on existing systems).
