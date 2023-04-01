.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _bind__ref_dnssec:

DNSSEC
======

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:


.. _bind__ref_dnssec_policies:

Policies
--------

If ``dnssec`` is enabled in :envvar:`bind__features`, the
:file:`/etc/bind/named.conf` file will contain a number of `DNSSEC policies`__,
which control the kind of keys to use for signing a given zone, including
details such as the validity of the keys and various timeouts.

.. __: https://bind9.readthedocs.io/en/latest/dnssec-guide.html#creating-a-custom-dnssec-policy

The default policies are (see :envvar:`bind__default_configuration`):

* ``csk``
* ``csk-rollover``
* ``kskzsk``
* ``kskzsk-rollover``

In general, keys in DNSSEC are used for one or both of the following roles: as
a Zone Signing Key (ZSK), used to protect all zone data; or as a Key Signing
Key (KSK), used to protect the ZSKs. The KSKs are typically longer-lived than
the ZSKs, as they need to be published in the parent zone, which may require
manual intervention and/or interaction with a registrar or registry (e.g. the
organization that you bought the domain from).

A key that is used for both roles is referred to as a Combined Signing Key
(CSK). Like the KSK, a CSK needs to be published in the parent zone.


.. _bind__ref_dnssec_enabling:

Enabling DNSSEC
---------------

DNSSEC has to be enabled on a per-zone basis by specifying a suitable policy
for the given zone in its ``options`` parameter, for example like this (see
:ref:`bind__ref_zones` for more details and complete examples):

.. code-block:: yaml

   bind__zones:

     - name: 'example.com'
       comment: 'My main domain'
       options:

         - name: 'dnssec-policy'
           value: '"kskzsk-rollover"'


.. _bind__ref_dnssec_rollover:

Key Rollover
------------
The ``*-rollover`` versions of the DNSSEC policies will create a CSK or KSK
which will automatically expire at certain intervals (default: one year) for
security reasons (for details, see e.g. :rfc:`6781` and :rfc:`7583`).
Sometime before the key expiry, BIND will generate a new CSK/KSK, which needs
to be published in the parent zone, and some time after the expiry, the old
CSK/KSK also needs to be removed from the parent zone.


.. _bind__ref_dnssec_rollover_automatic:

Automatic Key Rollover
~~~~~~~~~~~~~~~~~~~~~~
BIND includes a relatively new feature which can, in theory, automate this,
by publishing suitable `CDS and CDNSKEY`__ (:rfc:`8078`) resource records.
These resource records can be used by the parent zone to automatically update
its ``DS`` records.

.. __: https://bind9.readthedocs.io/en/latest/dnssec-guide.html#cds-cdnskey

Often, these records can also be used to enable/disable DNSSEC validation.
Whether they can do so, and under which circumstances is registry/registrar
specific (one common policy to enable DNSSEC for a previously unsigned zone
is that the ``CDS``/``CDNSKEY`` entries need to remain stable for 72 hours
and have to be identical for all name servers for a given zone).

Publishing the addition/removal of keys in the parent zone is the first half
of the automation puzzle. The second half is making BIND aware that the
(un)publication has been performed in the parent zone.

For this, the `parental-agents`__ configuration option can be used.
For each zone which uses ``CDS``/``CDNSKEY`` updates, a list of parent
zone server IP addresses needs to be provided. A list of IP addresses can
be obtained using :command:`dig` for the ``NS`` records of the parent zone.
Assuming the BIND role is configured to be authoritative for ``example.com``,
the parent zone would be ``com.``:

.. __: https://bind9.readthedocs.io/en/latest/dnssec-guide.html#working-with-the-parent-zone-2

.. code-block:: console

   # dig com. NS
   ...
   ;; ANSWER SECTION:
   com.			142479	IN	NS	a.gtld-servers.net.
   com.			142479	IN	NS	b.gtld-servers.net.
   ...
   ;; ADDITIONAL SECTION:
   a.gtld-servers.net.	142479	IN	A	<first IP addr>
   b.gtld-servers.net.	142479	IN	A	<second IP addr>
   ...
   a.gtld-servers.net.	142479	IN	AAAA	<first IPv6 addr>
   b.gtld-servers.net.	142479	IN	AAAA	<second IPv6 addr>
   ...

.. note::
   If :command:`dig` provides no ``ADDITIONAL`` section, you'll have to
   query the IP addresses separately using ``dig <fqdn> A`` and/or
   ``dig <fqdn> AAAA``.

All of, or some, of these IP addresses can then be added to a
``parental-agents`` block, either directly in the relevant zone(s):

.. code-block:: yaml

   bind__zones:

     - name: 'example.com'
       options:

         - name: 'parental-agents'
           options:

             - name: 'parent-1'
               raw: '<first IP addr>;'

             - name: 'parent-2'
               raw: '<second IP addr>;'

Or as a separate top-level option which can be reused in several zones:

.. code-block:: yaml

   bind__configuration:

     - name: 'parental-agents dot-com-agents'
       options:

         - name: 'parent-1'
           raw: '<first IP addr>;'

         - name: 'parent-2'
           raw: '<second IP addr>;'

   bind__zones:

     - name: 'example.com'
       options:

         - name: 'parental-agents'
           options:

             - name: 'parent-1'
               raw: '"dot-com-agents";'

The ``parental-agents`` for a given zone will be queried periodically by
BIND and if all the parental agents have the correct ``DS`` entries, the
key will automatically be considered (un)published once the time intervals
configured in the ``dnssec-policy`` have lapsed. This will also be reflected
in the logs produced by :command:`named`:

.. code-block:: console

   # journalctl -u named --since 12:00 | grep checkds
   Aug 15 18:34:41 test named[1102873]: zone example.com/IN/external-view: checkds: set 6 parentals
   Aug 15 18:34:42 test named[1102873]: keymgr: checkds DS for key example.com/ECDSAP256SHA256/12349 seen published at Mon Aug 15 18:34:42 2022

In theory, the ``parental-agents`` feature could also be used in conjunction
with the :ref:`bind__ref_dnssec_rollover_script` to not have to manually notify
BIND when the requested actions have been performed.

The ``parental-agents`` feature will hopefully be further developed and
automated in future BIND releases.


.. _bind_ref_dnssec_rollover_manual:

Manual Key Rollover
~~~~~~~~~~~~~~~~~~~

Unfortunately, many registries/registrars do not support automated key updates
via ``CDS``/``CDNSKEY`` records yet (a list which may or may not be accurate
is provided `here`__). As an alternative, this role includes a script which
will be executed periodically to check for keys which need to be (un)published
in the parent zone.

.. __: https://github.com/oskar456/cds-updates


.. _bind__ref_dnssec_rollover_script:

Rollover Script
~~~~~~~~~~~~~~~

The rollover script can be enabled/disabled via the
:envvar:`bind__dnssec_script_enabled` variable.

The script will run periodically (via :ref:`debops.cron`), and check
for keys which are to be published in, or removed from, the parent zone.

The configuration for the script is defined in the
``bind__dnssec_script_*_configuration`` variables, which will be merged and
used to create a configuration file in
:file:`/etc/bind/debops-bind-rollkey.json`.

.. note::
   If :envvar:`bind__dnssec_script_domains` has not been configured, the script
   will attempt to automatically determine all zones which need to be
   monitored. This currently requires dumping the complete zone database to
   a file and parsing the file. This can be both slow (depending on zone size)
   and error-prone, so a manual definition of the zones to monitor may be
   worthwhile.

Depending on how :envvar:`bind__dnssec_script_method` has been configured,
the script will perform different actions when it detects that a key change
needs to be performed:

``log``
  Key updates will simply be logged to a file, default
  :file:`/var/log/debops-bind-rollkey.log`. The administrator will have to
  perform the requested actions manually and will also have to notify BIND
  manually once the requested actions have been completed. This can be done
  using :command:`rndc` on the BIND host. This can be done by executing (on the
  BIND host):

  .. code-block:: console

     # rndc dnssec -checkds -key <key-id> -alg <key-alg> (published | withdrawn) zone [class [view]]

``email``
  Key updates will be requested via email. Like for ``log``, the administrator
  will have to notify BIND once the requested actions have been performed.

``external``
  An external script will be executed when keys need to be updated.
  Many registrars provide APIs which allow DNSSEC keys to be added/removed
  in a programmatic manner without user intervention (once suitable scripts
  have been initialized).
  The script will be called with six arguments:

  ``<action> <key-id> <key-alg> <zone> <class> <view>``

  Where:

  ``action``
    Describes the action which needs to be performed. Currently defined
    actions are: ``withdraw`` and ``publish``.

  ``key-id``
    The numeric ID of the key on which the ``action`` needs to be performed.

  ``key-alg``
    The numeric algorithm of the key on which the ``action`` needs to be
    performed.

  ``zone``
    The zone which the key belongs to.

  ``class``
    The class of the ``zone``. It is exceedingly unlikely that this will be
    anything else than ``IN``.

  ``view``
    The view which the ``zone`` belongs to. If no views are configured, the
    view will be ``_default``.

  If the script exits with a status of ``0``, the script will assume that the
  requested action was performed and will automatically notify BIND that
  the key(s) have been published/withdrawn.

  A suitable script will be expected to be located on the Ansible controller,
  in the ``files_path`` override directory defined in the :file:`debops.cfg`
  file (see :ref:`configuration`).

  For example, if :file:`.debops.cfg` reads:

  .. code-block:: none

     ...
     [override_paths]
     files_path = ansible/overrides/files
     ...

  Then the custom script should be placed in
  :file:`project-dir/ansible/overrides/files/usr/local/sbin/debops-bind-rollkey-action`


.. _bind__ref_dnssec_nsec:

NSEC vs NSEC3
-------------

DNSSEC provides two mechanisms for when the server has to sign replies
indicating that a particular resource record doesn't exist, ``NSEC`` and
``NSEC3``.

``NSEC`` is computationally less intensive than ``NSEC3``, but allows a
zone to be *walked* (i.e. for an attacker to determine all records in the
zone). ``NSEC`` also has no opt-out, so for a sparsely signed zone (e.g.
the ``.com`` TLD), the resulting zone files are *much* larger.

``NSEC3`` makes *zone walking* more difficult, at the cost of some
additional computational burden for the server. It also gives the server
the possibility to exclude some records (insecure delegations).

Whether DNSSEC signed zones should, by default, use ``NSEC3`` instead of
``NSEC`` is controlled by the :envvar:`bind__dnssec_use_nsec3` variable,
see the `BIND DNSSEC Guide`__ for more details.

.. __: https://bind9.readthedocs.io/en/latest/dnssec-guide.html#proof-of-non-existence-nsec-and-nsec3


.. _bind__ref_dnssec_csync:

CSYNC
-----

Another interesting possibility for automation which builds on DNSSEC is
``CSYNC`` (defined in :rfc:`7477`), which allows a child zone to automatically
update ``NS`` and, where applicable/supported, ``A`` and ``AAAA`` ("glue")
records in the parent zone without manual intervention.

This can be done by publishing a suitable ``CSYNC`` record in a DNSSEC
signed zone. For example:

.. code-block:: none

   example.com. 3600 IN CSYNC 66 3 NS A AAAA

Which would tell the parent zone that ``NS`` records (and the ``A``/``AAAA``
records for the nameservers) for the child zone should be automatically updated
by the parent zone, but only if the ``SOA`` serial number is at least ``66``.

Or, alternatively:

.. code-block:: none

   example.com. 3600 IN CSYNC 0 1 NS A AAAA

Which would tell the parent zone that the same records should be updated from
the child zone no matter what the ``SOA`` serial number is.

See :rfc:`7477` for further details and valid values for the ``CSYNC`` record.

Similarly to the ``CDS``/``CDNSKEY`` situation, most registries/registrars do
not yet support automated record updates in the parent zone via ``CSYNC``.


.. _bind__ref_dnssec_testing:

Testing DNSSEC
--------------

The DNSSEC status of a domain can be tested using the :command:`dig` tool.

First, make sure that ``DS`` and ``DNSKEY`` entries exist for the domain:

.. code-block:: console

   # dig DS example.com
   ...
   ;; ANSWER SECTION
   example.com.			3600	IN	DS	...
   ...

   $ dig DNSKEY example.com
   ...
   ;; ANSWER SECTION
   example.com.			3600	IN	DNSKEY	...

Next, try looking up a record using DNSSEC (using the ``+dnssec`` option):

.. code-block:: console

   # dig example.com A +dnssec
   ...
   ;; Got answer:
   ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 5638
   ;; flags: qr rd ra ad; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

   ;; OPT PSEUDOSECTION:
   ; EDNS: version: 0, flags: do; udp: 1232
   ;; QUESTION SECTION:
   ;example.com.		IN	A

   ;; ANSWER SECTION:
   example.com.		3600	IN	A	<some IP address>
   example.com.		3660	IN	RRSIG	A ...
   ...

The important parts are: the ``status: NOERROR``, that the ``flags:`` include
``ad`` (authentic data), and that the answer includes an ``RRSIG``.

For more details, see the :man:`dig(1)` man page.

Useful online tools for testing your DNSSEC configuration include:

* `DNSViz`__
* `DNSSEC Analyzer`__
* `Zonemaster`__

.. __: https://dnsviz.net/
.. __: https://dnssec-analyzer.verisignlabs.com/
.. __: https://zonemaster.iis.se/en/
