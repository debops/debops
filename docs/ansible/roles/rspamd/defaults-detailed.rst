.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.rspamd`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.


.. _rspamd__ref_configuration:

rspamd__configuration
---------------------

The ``rspamd__*_configuration`` variables define the contents of the
:file:`/etc/rspamd/local.d` and :file:`/etc/rspamd/override.d` configuration
directories. The variables are merged in the order defined by the
:envvar:`rspamd__combined_local_configuration` and
:envvar:`rspamd__combined_override_configuration` variables, which allows
modification of the default configuration through the Ansible inventory.

Note that files which are *not* configured via the ``rspamd__*_configuration``
variables will be deleted from the :file:`/etc/rspamd/local.d` and
:file:`/etc/rspamd/override.d` directories, to ensure that the ``Rspamd``
configuration is predictable.

See the ``Rspamd`` `configuration documentation`__ and, in particular, the
`modules documentation`__ for details on the possible configuration files
and the relevant parameters for each file.

.. __: https://rspamd.com/doc/configuration/index.html
.. __: https://rspamd.com/doc/modules/

Examples
~~~~~~~~

See the :envvar:`rspamd__default_local_configuration` and
:envvar:`rspamd__default_override_configuration` variables for examples of
existing configuration.

Configure another RBL (`Runtime Black List`__) check:

.. __: https://rspamd.com/doc/modules/rbl.html

.. code-block:: yaml

   rspamd__local_configuration:

     - file: 'rbl.conf'
       comment: |
         RBL configuration
         https://rspamd.com/doc/modules/rbl.html
       options:

         - name: 'rules'
           options:

             - name: 'SIMPLE_RBL'
               options:

                 - name: 'rbl'
                   value: 'rbl.example.net'

                 - name: 'checks'
                   value: [ 'from' ]

This will result in :file:`/etc/rspamd/local.d/rbl.conf` being created with
the following content:

.. code-block:: none

   ...
   rules {
       SIMPLE_RBL {
           rbl = "rbl.example.net";
           checks = ["from"];
       }
   }


.. _rspamd__ref_configuration_syntax:

Syntax
~~~~~~

The variables contain a list of YAML dictionaries, each dictionary can have
the following parameters:

``file``
  Required. Name of the file to create in the :file:`/etc/rspamd/local.d`
  or :file:`/etc/rspamd/override.d` directory. This parameter is used as an
  "anchor", configuration entries with the same ``file`` are combined together
  and affect each other in order of appearance.

``comment``
  Optional. This parameter can be used to provide a short description
  which will be included in the generated configuration file.

``state``
  Optional. If not specified or ``present``, the configuration file will be
  generated. If ``absent`` or ``init``, the configuration file will not be
  generated and if any old configuration file with the same name exists
  on the target host, it will be removed. If ``ignore``, the configuration
  file will not be generated and old configuration files, if any, will not
  be removed.

``weight``
  Optional. A positive or negative number which can be used to affect the order
  of files to be generated. Positive numbers add more "weight" to the section
  making it appear "lower" in the list; negative numbers subtract the "weight"
  and therefore move the file up in the list.

``options``
  Required. A list of :command:`rspamd` configuration options for a given
  file. The ``options`` parameters from configuration entries with the same
  ``file`` parameter are merged together in order of appearance and can
  affect each other.

  Note that the ``options`` parameters can be used recursively to generate
  configuration blocks of arbitrary depth (as illustrated in the example
  above).

  The options can be specified in a simple form as key/value pairs, where the
  key is the option name and value is the option value. Alternatively, if the
  ``name`` and ``value`` parameters are used, the entries can use an extended
  format with specific parameters:

  ``name``
    Required. The name of a given :command:`rspamd` configuration option
    for a given ``file``. Options with the same ``file`` and ``name``
    will be merged in order of appearance.

  ``value``
    Either ``value`` or ``options`` is required. This defines the value of a
    given configuration option. It can be either a string, a boolean, a number,
    or a YAML list.

  ``options``
    Either ``value`` or ``options`` is required. This parameters takes a list
    of configuration sub-options, thus allowing ``options`` to be used
    recursively to generate configuration blocks of arbitrary depth (as
    illustrated in the example above).

  ``raw``
    Optional. String or YAML text block which will be included in the
    configuration file "as is". If this parameter is specified, the ``name``
    and ``value`` parameters are ignored - you need to specify the
    entire line(s) with configuration option names as well.

  ``state``
    Optional. If not defined or ``present``, a given configuration option or
    section will be included in the generated configuration file. If ``absent``,
    ``ignore`` or ``init``, a given configuration option or section will not be
    included in the generated file. If ``comment``, the option will be included
    but commented out and inactive.

  ``comment``
    Optional. String or YAML text block that contains comments about a given
    configuration option.


.. _rspamd__ref_dkim:

DKIM
----
`DomainKeys Identified Mail (DKIM)`__ is an email authentication method
designed to sign outgoing messages using keys which are published in the
DNS zone of the sending domain. This allows the recipient to check that
a received email was indeed sent from the given domain.

:command:`rspamd` includes support for both checking DKIM signatures and
for generating DKIM signatures for outgoing email messages. In order to do
the signing, suitable keys have to be generated and published in the right
DNS zone(s). In addition, the keys used for signing the emails should be
replaced on a regular basis (as explained e.g. `in this document`__), a
process which is often referred to as *key rollover*.

Unfortunately, the step of publishing/removing DNS records cannot be fully
automated as there is no universal means for doing so, neither in the generic
case, nor in DebOps. The support for DKIM signing therefore defaults to
being disabled in the :ref:`debops.rspamd` role, but the recommendation is
to go through the steps of manually enabling and configuring it.

In order to simplify this task, the :ref:`debops.rspamd` role includes two
tools, :file:`rspamd-dkim-keygen` and :file:`rspamd-dkim-update` which,
after some initial configuration, can automate the key rollover process.

To enable DKIM signing, first check that :envvar:`rspamd__dkim_domains` lists
all the domains that will be used to send email and then override the
:envvar:`rspamd__dkim_enabled` parameter:

.. __: https://en.wikipedia.org/wiki/DomainKeys_Identified_Mail
.. __: http://www.m3aawg.org/DKIMKeyRotation

.. code-block:: yaml

   rspamd__dkim_enabled: True

   rspamd__dkim_domains: [ "example.com", "example.net" ]


.. _rspamd__ref_dkim_keygen:

rspamd-dkim-keygen
~~~~~~~~~~~~~~~~~~

The :file:`rspamd-dkim-keygen` script takes care of generating keys for the
domains listed in :envvar:`rspamd__dkim_domains` and will be executed on a
monthly basis via a :command:`cron` job. The configuration for
:file:`rspamd-dkim-keygen` is stored in :file:`/etc/rspamd/dkim-keygen.json`,
which is controlled via the ``rspamd__dkim_keygen_*_configuration`` variables.
These variables are merged in the order defined by the
:envvar:`rspamd__dkim_keygen_combined_configuration` variable, which allows
modification of the default configuration through the Ansible inventory in a
manner similar to the :ref:`rspamd__ref_configuration` and with a simplified
version of the :ref:`rspamd__ref_configuration_syntax`, since ``options`` are
not supported.

In the default configuration, ``RSA`` and ``ed25519`` keys will be generated in
:file:`/var/lib/rspamd/dkim/`. Three time periods are defined by the
``future_period``, ``active_period`` and ``expired_period`` (in months). These
are the stages of the key rollover that keys go through. Keys are generated
``future_period`` number of months before they are made active (in order to
allow for the keys to be published in the DNS). Then they are in active use
(i.e. used to sign outgoing emails) during the ``active_period``. Finally, keys
enter the ``expired_period`` where they are no longer used to sign emails (but
the records are still published in the DNS to make sure that in-flight emails
are still valid). Finally, upon expiry of the ``expired_period``, when no
emails should be in-flight any more, the keys can be archived (to
:file:`/var/lib/rspamd/dkim-archive/` and removed from the DNS.

The one exception is when :command:`rspamd-dkim-keygen` is first executed
(usually the first time the :ref:`debops.rspamd` role is run for a given host),
in which case the initial keys will immediately go live.

Whenever :command:`rspamd-dkim-keygen` detects that a new key should be
published in the DNS, or that a stale key needs to be removed, it will call out
to the complimentary tool :command:`rspamd-dkim-update`.


.. _rspamd__ref_dkim_update:

rspamd-dkim-update
~~~~~~~~~~~~~~~~~~

The :file:`rspamd-dkim-update` script takes care of publishing/removing DNS
resource records for DKIM keys generated/expired by the :file:`rspamd-dkim-keygen`
script.

The most important variable for :file:`rspamd-dkim-update` is the
:envvar:`rspamd__dkim_update_method`, which defaults to sending emails to
the administrator for manual handling of DNS updates.

In the alternative, the process can be automated using the :command:`nsupdate`
tool. This requires configuration changes to the DNS server (e.g.
:command:`bind`), either to trust the IP address of the :command:`rspamd` host
(not recommended), or to generate suitable keys (for example, `TSIG keys`__)
and to configure these keys to have the appropriate permissions to add/remove
DNS resource records (for example, using :command:`bind`'s fine-grained
`update-policy options`__). Alternatively, the server can be configured to allow
a given `Kerberos principal`__ to perform updates (in which case a ``keytab``
needs to be generated instead of a ``TSIG`` key file and the references to the
key file below should then be read as referring to the ``keytab`` file).

The key file needs to be stored on the :command:`rspamd` host, by default at
:file:`/etc/rspamd/dkim_dns_key` (preferably with ``0640`` permissions and
``root:_rspamd`` ownership). This can be automated by transferring the key
file to the Ansible controller and putting it in the appropriate override
directory (e.g. :file:`project-dir/ansible/overrides/files/etc/rspamd/dkim_dns_key` as
explained below in the :ref:`rspamd__ref_dkim_override` section).

Once the keyfile has been prepared, check the values of ``nsupdate_*`` in the
configuration for :file:`rspamd-dkim-update`, stored in
:file:`/etc/rspamd/dkim-update.json`, which is controlled via the
``rspamd__dkim_update_*_configuration`` variables.  These variables are merged
in the order defined by the
:envvar:`rspamd__dkim_update_combined_configuration` variable, which allows
modification of the default configuration through the Ansible inventory in a
manner similar to the :ref:`rspamd__ref_configuration` and with a simplified
version of the :ref:`rspamd__ref_configuration_syntax`, since ``options`` are
not supported.

.. __: https://bind9.readthedocs.io/en/latest/advanced.html#tsig
.. __: https://bind9.readthedocs.io/en/latest/reference.html#dynamic-update-policies
.. __: https://bind9.readthedocs.io/en/latest/advanced.html#dynamic-update


.. _rspamd__ref_dkim_override:

Overriding rspamd-dkim-keygen/update
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The reason why there are two separate scripts for key generation and DNS
updates is that it allows the administrator to override the default scripts by
providing their alternative script in the ``files_path`` override directory
defined in the :file:`.debops.cfg` file (see :ref:`configuration`).

For example, if :file:`.debops.cfg` reads:

.. code-block:: none

   ...
   [override_paths]
   files_path = ansible/overrides/files
   ...

Then the custom script(s) should be placed in
:file:`project-dir/ansible/overrides/files/usr/local/sbin/rspamd-dkim-update`
and/or
:file:`project-dir/ansible/overrides/files/usr/local/sbin/rspamd-dkim-keygen`.
