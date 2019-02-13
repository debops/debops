Default variable details
========================

Some of ``debops.preseed`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _preseed__ref_configs:

preseed__configs
----------------

This is a list of Preseed configuration files offered by the webserver to the
clients.

To make custom changes easier, preseed configuration file as well as the
post-install script have default stored in the templates themselves, a subset
of the available default variables is exposed in the :file:`defaults/main.yml`
file, however more esoteric variables were left out to keep the list of
variables short.

You can also configure the Preseed files using dict keys and values, the
variable naming scheme is::

    preseed__debian_<key> - item.<key>

Some more important keys:

``name``
  Name of the Preseed configuration, should be limited to alphanumeric
  characters and a hyphen (``-``) character. Will be used in the DNS do export
  the configuration to the clients

``type``
  Specify the set of Preseed templates to use for this configuration.
  Determines among other things the distribution which will be configured

``release``
  Specify the distribution release to configure. By default the current host
  release is used if none is specified

Examples
~~~~~~~~

Example Preseed configuration with custom mirror and list of additional
packages to install::

    preseed__configs:

      - name: 'debian-mail'
        release: 'wheezy'
        mirror_hostname: 'ftp.us.debian.org'
        packages: [ 'postfix', 'dovecot-imapd', 'mutt' ]

