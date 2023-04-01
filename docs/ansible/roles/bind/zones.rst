.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _bind__ref_zones:

Zones and Views
===============

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:


.. _bind__ref_zones_introduction:

Introduction
------------

The ``bind__*_zones`` variables (not to be confused with the
``bind__*_generic_zones`` variables, see the next section) define the zones
which should be maintained via Ansible (and which are made available for use
in the ``bind__*_configuration`` variables using the autovalue feature, see
the corresponding :ref:`bind__ref_configuration_syntax`).

The toplevel items in the ``bind__*_zones`` lists must be dicts containing
either ``name`` keys (for zones) or ``view`` keys (in case you are using
`views`__, also known as *split-horizon* DNS, see :rfc:`6950`). Each ``view``
can, in turn, contain a number of zones, defined in its ``zones`` parameter.

.. __: https://bind9.readthedocs.io/en/latest/reference.html#view-block-definition-and-usage

.. warning::
   Mixing ``view`` and ``name`` entries at the top level will result in an
   error during the execution of the role. Either all zones need to be in
   a view, or all of them need to be outside any view.


.. _bind__ref_zones_generic:

Generic Zones
-------------

The ``bind__*_generic_zones`` is similar to ``bind__*_zones``, but define zones
which should be present in every view.  They will automatically be added to
every view (if you are using views), or simply added at the end of the list of
zones (if you are not using views). That also means that you cannot define
``view`` items in ``bind__*_generic_zones``.

Other than that, the configuration syntax for ``bind__*_generic_zones`` is the
same as that of ``bind__*_zones``, and the following sections are equally
applicable to both sets of variables.


.. _bind__ref_zones_content:

Zone content
------------

The role can be used to define the initial content of zones and to
automatically generate the corresponding zone files for BIND to use.  This is
controlled using the ``content`` parameter. If you already have zone files at
hand, or plan to use some alternative source of zone files (including
hand-written zone files which could be transferred to the remote host running
BIND using e.g. the :ref:`debops.resources` role), the ``content`` parameter
should *not* be defined for a zone.

.. note::
   As a minimum, BIND expects a valid zone to contain a ``NS`` record. Zones
   lacking such a resource record will result in :command:`named` logging an
   error and not loading the zone. If you want to create an empty zone, you
   should therefore set ``content`` to something like ``@ IN NS localhost.``.
   If the nameserver is in the zone itself, it also needs at least one ``A``
   or ``AAAA`` record.


.. _bind__ref_zones_dynamic:

Dynamic zone updates
--------------------

BIND supports dynamic zone updates if the `update-policy`__ or `allow-update`__
options have been defined for a zone. By default, any updates to a zone file
are written by the :command:`named` daemon to a separate *journal* file (by
default, the same path as the zone file, with an additional ``.jnl``
extension).

.. __: https://bind9.readthedocs.io/en/latest/reference.html#namedconf-statement-update-policy
.. __: https://bind9.readthedocs.io/en/latest/reference.html#namedconf-statement-allow-update

The changes which are stored in the separate journal files can, and will,
be merged back into the original zone file (see, e.g. the ``sync`` command for
the :man:`rndc` utility, but :command:`named` will also automatically sync
changes at various points in time, e.g. during restarts).

.. warning::
   This means that a zone file and its journal file can get out of sync
   if the zone file is changed from an outside tool, like Ansible/DebOps,
   while there are unmerged changes in the zone's journal file. That, in
   turn, may lead to BIND refusing to load the zone on restart.

   Enabling DNSSEC means that BIND will also update the zone on its own,
   for example, to add signing records. In other words, there are many
   different ways in which a zone might be dynamic.

While the role attempts to minimise the risk of creating such inconsistencies,
it can never be guaranteed in the presence of both dynamic and "static" zone
changes. The recommended approach is therefore to *always* perform dynamic
updated on dynamic zones, e.g. using :command:`nsupdate` (which can make use
of :ref:`bind__ref_keys` to authenticate requests). For example (this example
assumes that it is executed on the Ansible controller):

.. code-block:: console

   # nsupdate -k ansible/secret/bind/foobar/debops-key.key
   > server foobar.example.com
   > ttl 3600
   > zone example.com
   > delete oldhost.example.com A
   > add newhost.example.com A 192.168.2.99
   > send
   > quit

See :man:`nsupdate(1)` for further details and examples.


.. _bind__ref_zones_views:

Further remarks on using views
------------------------------

Note that if you use views, some options may have to be moved from the toplevel
option block in :file:`/etc/bind/named.conf` to the per-view equivalent.

For example, if you use the :envvar:`bind__blocked_domains` feature together
with views, you may define something like this in the Ansible inventory (in
effect, moving the ``response-policy`` option and ``rpz.local`` zone down from
the global to the view level):

.. code-block:: yaml

   bind__configuration:

     - name: 'options'
       options:

         - name: 'response-policy-blocked-domains'
           state: 'absent'

   bind__default_zones: []

   bind__zones:

     - view: 'internal-view'
       options:

         - name: 'response-policy-blocked-domains'
           raw: 'response-policy { zone "rpz.local"; } break-dnssec yes;'

       zones:

         - name: 'rpz.local'
           options:

             - name: 'type'
               value: 'master'

             - name: 'file'
               autovalue: 'zone_file_path'

           content: ...


.. _bind__ref_zones_examples:

Examples
--------

See :envvar:`bind__default_generic_zones` for some simple examples.

A more complex example (without a ``view``) could look something like this:

.. _bind__ref_zones_examples_noview:

.. code-block:: yaml

   bind__zones:

     - name: 'example.com'
       comment: 'My main domain'
       options:

         - name: 'type'
           value: 'master'

         - name: 'allow-transfer'
           options:

             - name: 'allow-transfer-1'
               raw: '192.168.1.2; 192.168.1.3;'

         - name: 'update-policy'
           options:

             - name: 'update-policy-local-ddns'
               raw: 'grant local-ddns zonesub any;'

             - name: 'update-policy-debops'
               raw: 'grant debops-key zonesub any;'

         - name: 'dnssec-policy'
           value: '"kskzsk-rollover"'

       content:

.. _bind__ref_zones_examples_view:

Here's an example using multiple ``view`` entries, DNSSEC, and multiple keys to
differentiate between the views:

.. code-block:: yaml

   bind__keys:

     - name: 'internal-key'
       type: 'tsig'
       algorithm: 'hmac-sha512'

     - name: 'external-key'
       type: 'tsig'
       algorithm: 'hmac-sha512'

   bind__configuration:

     - name: 'acl-internal'
       option: 'acl internal-acl'
       comment: 'ACL matching internal users'
       options:

         - name: 'not-external-key'
           raw: '!key external-key;'

         - name: 'internal-key'
           raw: 'key internal-key;'

         - name: 'internal-ipv4'
           raw: '192.168.1.0/24;'

         - name: 'internal-ipv6'
           raw: 'fd27:f00f:f00f::/48;'

         - name: 'internal-localhost'
           raw: 'localhost;'

     - name: 'acl-external'
       option: 'acl external-acl'
       comment: 'ACL matching external users'
       options:

         - name: 'not-internal-key'
           raw: '!key internal-key;'

         - name: 'external-key'
           raw: 'key external-key;'

         - name: 'any'
           raw: 'any;'

   bind__zones:

     - view: 'internal-view'
       comment: 'Internal view'
       options:

         - name: 'match-clients'
           options:

             - name: 'internal-acl'
               raw: 'internal-acl;'

         - name: 'allow-recursion'
           options:

             - name: 'internal-acl'
               raw: 'interal-acl;'

       zones:

         - name: 'example.com'
           comment: 'My main domain'
           options:

             - name: 'type'
               value: 'master'

             - name: 'allow-transfer'
               options:

                 - name: 'allow-transfer-1'
                   raw: '192.168.1.2; 192.168.1.3;'

             - name: 'update-policy'
               options:

                 - name: 'update-policy-local-ddns'
                   raw: 'grant local-ddns zonesub any;'

                 - name: 'update-policy-debops'
                   raw: 'grant debops-key zonesub any;'

             - name: 'dnssec-policy'
               value: '"kskzsk"'

           content: ...


.. _bind__ref_zones_view_syntax:

View syntax
~~~~~~~~~~~

Views are defined using a list of YAML dictionaries as toplevel items in the
``bind__*_zones`` variables. The following keys are valid in a ``view`` dict:

``view``
  Required, string. Name of a given view. Multiple views with the same ``view``
  are merged together.

``state``
  Optional, string. If not specified or ``present``, a given view will be
  present in the generated configuration. Otherwise, the view will not be
  included in the generated configuration.

``comment``
  Optional, string. A comment for the view which will be included in the
  generated configuration for documentation purposes.

``zones``
  Optional, list of YAML dictionaries defining zones belonging to the given
  view. See :ref:`bind__ref_zones_zone_syntax`.

``options``
  Optional, list of YAML dictionaries defining options for the given view.
  The possible configuration options are listed `here`__ and the valid dict
  parameters are the same as for
  :ref:`bind__*_configuration<bind__ref_configuration_syntax>`.

  .. __: https://bind9.readthedocs.io/en/latest/reference.html#view-block-grammar


.. _bind__ref_zones_zone_syntax:

Zone syntax
-----------

Configuration sections are defined using a list of YAML dictionaries, each
dictionary uses specific parameters:

``name``
  Required, string. Name of a given zone (with or without a trailing period),
  this must be a valid domain name (e.g. ``example.com``). Multiple
  configuration entries with the same ``name`` are merged together.

``comment``
  Optional, string. A comment for the zone which will be included in the
  generated configuration for documentation purposes.

``state``
  Optional, string. If not specified or ``present``, a given zone will be
  present in the generated configuration. Otherwise, the zone will not be
  included in the generated configuration.

``dir``
  Optional, string. The directory in which the zone file should be created.
  Defaults to :file:`/var/lib/bind/<view>/<zone>/`. Note that changing the
  default may clash with security policies defined by e.g. ``AppArmor``.
  Has no effect unless ``content`` has been defined.

``owner``
  Optional, string. The UNIX user owning the zone file. Defaults to ``root``.
  Has no effect unless ``content`` has been defined.

``group``
  Optional, string. The UNIX group owning the zone file. Defaults to ``bind``.
  Has no effect unless ``content`` has been defined.

``mode``
  Optional, octal mode string. The mode of the zone file. Defaults to ``0775``.
  Has no effect unless ``content`` has been defined.

``force``
  Optional, boolean. Whether an existing zone file should be overwritten if
  the ``content`` (see below) has changed. Default: ``False``. Changing the
  default value can have undesirable consequences if dynamic updates are also
  enabled for the zone (see :ref:`bind__ref_zones_dynamic` for details).
  Has no effect unless ``content`` has been defined.

``ttl``
  Optional, string or integer. The default ``TTL`` of the zone. Integers
  define a TTL in seconds, while a string can be used to define a TTL in
  a more human-readable format (e.g. ``1d``, ``2m``, ``1h``).

``origin``
  Optional, string. This can be used to define the domain name which a
  given zone is for. If not defined (recommended), the ``name`` will be
  used as the ``origin`` for the zone.

``soa_primary``
  Optional, string. The primary server for this zone. Must be a valid domain
  name. If not defined, :envvar:`bind__default_zone_soa_primary` is used.

``soa_email``
  Optional, string. The email address of the person responsible for the zone.
  If not defined, :envvar:`bind__default_zone_soa_email` is used.

``soa_serial``
  Optional, string or integer. The serial number of the zone (a number which
  changes every time the zone is modified, and which is automatically
  incremented by the :command:`named` server in response to dynamic updates).
  If not defined, :envvar:`bind__default_zone_soa_serial` is used.

``soa_refresh``, ``soa_retry``, ``soa_expire``, ``soa_neg_ttl``
  Optional, string or integer. These values have the same format as the ``ttl``
  value and are used to complete the `SOA`__ record for the zone. If not
  defined, the defaults from ``bind__default_zone_soa_*`` are used.

  .. __: https://en.wikipedia.org/wiki/SOA_record

``options``
  Optional, list of YAML dictionaries defining options for the given zone.
  The format is the same as for the ``options`` parameter for views (see
  the :ref:`bind__ref_zones_view_syntax` above). Valid configuration options
  can be found `here`__ and the valid dict parameters are the same as for
  :ref:`bind__*_configuration<bind__ref_configuration_syntax>`.

  .. __: https://bind9.readthedocs.io/en/latest/reference.html#zone-block-grammar

``content``
  Optional, string or a list of strings/dicts. The resource records which
  should be present in the zone file in addition to the ``SOA`` record (which
  is always present). If this value is defined (even as an empty list), the
  zone file will be generated for a ``present`` zone. If defined as a string or
  list of strings, the string(s) will be added as-is to the zone file.

  If defined as a list of dicts, the valid dict options are:

  ``name``
    Required, string. Name of a given resource record. Multiple resource
    records with the same ``name`` are merged together. Note that a resource
    record which doesn't end with a period will be interpreted by BIND as
    being a relative record and have the zone's ``origin`` appended to it
    (so, assuming an ``origin`` of ``example.com.``, ``test.example.com`` will
    be interpreted as ``test.example.com.example.com.`` while ``test`` or
    ``test.example.com.`` will both refer to ``test.example.com.``).

  ``state``
    Optional, string. If not specified or ``present``, the resource record will
    be present in the generated configuration. If ``comment``, the resource
    record will be present but commented out. Any other value means that the
    resource record will not be included in the generated zone file.

  ``comment``
    Optional, string. A comment to include before the resource record in the
    zone file.

  ``raw``
    Optional, string. A string which will be included verbatim in the zone
    file. If this option is defined, the options below will be ignored.

  ``owner``
    Optional, string. The owner (read: name) of the resource record. If not
    defined, ``name`` will be used as the owner/name of the resource record.

  ``ttl``
    Optional, string or integer. The TTL of the resource record (defined in
    the same way as the zone ``ttl`` above).

  ``class``
    Optional, string. The class of the resource record. It is quite unlikely
    that any other class than ``IN`` (the default) is desired.

  ``type``
    Required, string. The type of the resource record (e.g. ``A``, ``AAAA``,
    or ``CNAME``).

  ``value``, ``rdata``
    Required, string. The data for the resource record (e.g. ``192.168.2.1``
    for a record of type ``A``). ``value`` and ``rdata`` are synonyms.
