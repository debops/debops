Getting started
===============

.. contents:: Sections
   :local:

Support for different PHP versions
----------------------------------

The ``debops.php`` role supports management of multiple PHP versions; only one
PHP version can be managed at a time. By default the role will install and
configure the PHP version provided with the current OS release.

The role checks for existence of ``php7.3``, ``php`` and ``php5.6`` APT
packages (by default in that order) and based on available versions installs
either ``php7.3-*``, the version preferred by the ``php`` package or
``php5.6-*`` APT packages. If multiple versions of the PHP packages are
available, the first found one wins. To force an older version in case the
newer one is installed, you can change the order of the packages used for the
version detection using the :envvar:`php__version_preference` list.

To learn how to specify different PHP packages for installation, refer to
:ref:`php__ref_packages` documentation.


.. _php__ref_sury:

PHP packages provided by Ondřej Surý
------------------------------------

`Ondřej Surý <https://qa.debian.org/developer.php?login=ondrej%40debian.org>`_
is a member of the Debian PHP Maintainers team and maintains Debian
`PHP5 <https://packages.qa.debian.org/p/php5.html>`_ and
`PHP7 <https://packages.qa.debian.org/p/php7.0.html>`_ packages. He also provides
`an external APT package repository <https://deb.sury.org/>`_ of PHP5 and PHP7
packages (among other things) for Debian and Ubuntu distributions.

The ``debops.php`` role can use the packages from the Ondřej Surý repositories
to provide PHP7 packages on Debian Jessie. Remember that these packages
**DO NOT** fall under the Debian Stable security support and may contain bugs.

To enable the custom APT repository, add in the Ansible inventory:

.. code-block:: yaml

   php__sury: True

This will add the required OpenPGP keys and APT repositories. The order of the
package versions should ensure that the PHP7 packages will be installed on
Debian Jessie.


Custom environment role
-----------------------

The ``debops.php`` provides a small, custom role ``debops.php/env`` which
should be added to the playbook or role dependencies before the main role and
other roles that use configuration from ``debops.php``, like
:ref:`debops.logrotate`. The ``debops.php/env`` role configures custom APT
repositories if they are enabled and prepares the facts needed by other roles
to function correctly. See the :ref:`provided playbook <php__ref_example_playbook>`
to see an example usage.


PHP Composer installation
-------------------------

The :ref:`debops.php` role will install the `PHP Composer`__, a dependency
manager for PHP. The version from the OS repositories will be preferred. On
older OS releases (including Debian Stretch), a known upstream binary will be
downloaded and installed instead.

.. __: https://getcomposer.org/


Layout of the php.ini configuration
-----------------------------------

The main :file:`/etc/php{5,/7.0}/*/php.ini` files maintained by the OS distribution
are not modified by the ``debops.php`` role to allow an easy upgrade process.
Instead, a custom :file:`php.ini` configuration is stored in
:file:`/etc/php{5,/7.0}/ansible/*.ini` files generated using a simple template,
which are then linked to each of the PHP SAPI directories in
:file:`/etc/php{5,/7.0}/*/conf.d/` which are read by the PHP interpreters. This
allows for configuration synchronization between different PHP interpreters. To
learn more about this process refer to :ref:`php__ref_configuration`
documentation.


Information stored in Ansible local facts
-----------------------------------------

The PHP version configured on a host is available for other Ansible roles
through the Ansible local facts. The specific variables are:

``ansible_local.php.version``
  Short version of the PHP environment, used in package names.
  Either ``5`` or ``7.0``.

``ansible_local.php.long_version``
  Longer version of the PHP environment, used for version comparison. For
  example, ``5.6.22`` or ``7.0.8``. This variable might be inaccurate in case
  of the minor or major version upgrade.

The Ansible local facts are used by the ``debops.php`` role to ensure
idempotent operation. In case that you want to upgrade a host to a newer PHP
release without uninstalling the older one, you can set :envvar:`php__reset` to
``True``, so that the role can re-detect the available PHP versions.
After one role run, you should set :envvar:`php__reset` back to its default
value.

Example inventory
-----------------

To enable management of a PHP environment on a host, you need to include that
host in the ``[debops_service_php]`` Ansible inventory group::

  [debops_service_php]
  hostname

The default configuration included in the role will install the base PHP
``cli`` and ``fpm`` packages and create a PHP-FPM pool meant to be used by the
``www-data`` user which is a common user account used to serve PHP applications
packaged on Debian systems. To deploy your own applications you should consider
creating a custom system account and a corresponding PHP-FPM pool to securely
separate it from other applications. To learn how to do that, refer to the
:ref:`php__ref_pools` documentation.


.. _php__ref_example_playbook:

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.php`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/php.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::php``
  Main role tag, should be used in the playbook to execute all tasks.

``role::php:config``
  Generate the PHP and PHP-FPM configuration.

``role::php:pools``
  Generate only PHP-FPM pool configuration.
