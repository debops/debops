.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _bind__ref_configuration:

Main configuration
==================

Some of the ``debops.bind`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _bind__ref_configuration_features:

Features
--------

The :envvar:`bind__features` variable control which BIND features should be
enabled. Valid values are (case-sensitive):

* ``dns`` - Regular DNS service (not including this feature is likely to lead
  to a broken configuration).
* ``dnssec`` - DNSSEC signed zones.
* ``dot`` - DNS over TLS.
* ``doh_https`` - DNS over HTTPS.
* ``doh_http`` - DNS over HTTP.
* ``doh_proxy`` - DNS using a web server as a proxy frontend.
* ``status_proxy`` - Provide server statistics over a proxy frontend.

The various features (except ``dns``) are explained in the
:ref:`bind__ref_dnssec` and :ref:`bind__ref_dot_doh` sections.

These features are used to provide reasonable defaults in the various
configuration templates.


.. _bind__ref_configuration_variables:

Variables
---------

The ``bind__*_configuration`` variables are used to create the main
configuration file :file:`/etc/bind/named.conf`. In the default configuration,
the zones, keys, etc defined in the separate ``bind__*_zones`` (see
:ref:`bind__ref_zones`) and ``bind__*_keys`` (see :ref:`bind__ref_keys`)
variables will be inserted into the generated configuration at the appropriate
places using ``autovalue`` parameters (described below in the
:ref:`bind__ref_configuration_syntax` section).


.. _bind__ref_configuration_examples:

Examples
--------

For a detailed example which makes use of all of the features offered by
the syntax, see the :envvar:`bind__default_configuration`.

Enable the use of ``forwarders`` (default nameservers which queries are
forwarded to in case the local installation of BIND doesn't know the answer,
such as an upstream ISP nameserver or one of the public nameservers operated
by companies such as Cloudflare, Google, etc):

.. code-block:: yaml

   bind__configuration:

     - name: 'options'
       options:

         - name: 'forwarders'
           state: 'present'
           options:

             - name: 'forwarder-1'
               raw: '8.8.8.8'

.. code-block:: yaml

This will result in a configuration file along the lines of:

.. code-block:: none

   options {
           ...
           forwarders {
                   1.1.1.1;
           }
           ...
   }

Change the lifetime of the KSK in the "kskzsk-rollover" policy:

.. code-block:: yaml

   bind_configuration:

     - name 'dnssec-policy-kskzsk-rollover'
       options:

         - name: 'keys'
           options:

             - name: 'ksk'
               comment: 'Original: key-directory lifetime 365d algorithm ecdsap256sha256'
               value: 'key-directory lifetime 6m algorithm ecdsap256sha256'


.. _bind__ref_configuration_syntax:

Syntax
------

Configuration options are defined using a list of YAML dictionaries, each
dictionary uses specific parameters, most of which follow well-known
:ref:`universal_configuration` patterns:

``name``
  Required, string. Name of a given option. Multiple configuration options
  with the same ``name`` are merged together. If the ``option`` parameter
  is specified, it will be used rather than ``name`` as the configuration
  option name.

``option``
  Optional, string. This can be used to override the default configuration
  option name (i.e. ``name``). This is useful when the same option needs to
  appear more than once in the configuration (in which case each instance can
  have the same ``option`` value, but a different ``name``).

``comment``
  Optional, string. A comment for the option which will be included in the
  generated configuration for documentation purposes.

``state``
  Optional, string. If not specified or ``present``, a given option will be
  present in the generated configuration. If ``absent``, ``init`` or
  ``ignore``, the option will not be present in the generated configuration.
  If ``comment``, the option will be present, but commented out (that also
  carries over to sub-configuration options defined in ``options``).

``raw``
  Optional, string. If defined, this parameter will be included verbatim in
  the generated configuration, ignoring ``name``, ``option``, ``options``,
  and ``value``.

``separator``
  Optional, boolean. If ``True``, an extra blank line will be inserted before
  the option in the configuration file for increased readability.

``value``
  Optional, string. The value of the option to be included in the generated
  configuration file.

``autovalue``
  Optional, string. Instead of a verbatim configuration ``value``, the
  role templates can generate automatic values.

  Currently supported autovalues are:

  ``keys``
    Will generate a list of keys defined using the ``bind__*_keys`` variables
    (see :ref:`bind__ref_keys`).

  ``zones``
    Will generate and include configuration for all views/and zones defined
    using the ``bind__*_zones`` and ``bind__*_generic_zones`` variables
    (see :ref:`bind__ref_zones`).

  ``zone_file_path``
    The absolute path to the zone file for a given zone. This generally only
    makes sense in the ``bind__*_zones`` variables (see
    :ref:`bind__ref_zones_zone_syntax`).

``options``
  Optional, list of YAML dicts. This can be used to define a number of
  sub-options. The YAML dicts of sub-options follow the same syntax as
  defined in this section and can be used to create the nested configuration
  hierarchy used in the :file:`/etc/bind/named.conf` syntax.
