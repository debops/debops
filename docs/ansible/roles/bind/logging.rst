.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _bind__ref_logging:

Logging
=======

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:


.. _bind_ref_logging_intro:

Introduction
------------

The BIND server by default logs a lot of information about misconfigured
clients, bad requests and misconfigured or misbehaving remote servers.
In most cases, there is little to nothing the administrator can do about
any of that. The BIND configuration syntax provides the possibility for
a fine-grained control over which kinds of messages gets logged when and
to where using the `logging`__ block.

.. __: https://bind9.readthedocs.io/en/latest/reference.html#logging-block-grammar

The role includes an example of a logging configuration (disabled by default)
which would redirect less relevant client/remote server messages to separate log
files, which hopefully means that the main logs (i.e. the output from
:command:`journalctl -u named`) remains relevant.


.. _bind__ref_logging_example:

Examples
--------

In order to enable the example logging configuration defined in the role
(in :envvar:`bind__default_configuration`), define something like this in the
inventory:

.. code-block:: yaml

   bind__configuration:

     - name: 'logging'
       state: 'present'

The relevant parts of :envvar:`bind__default_configuration` read something like
this:

.. code-block:: yaml

   bind__default_configuration:

     - name: 'logging'
       options:

         - name: channel client_spam_channel'
           options:

             - name: 'file'
               value: '"/var/log/bind/named_recent_client.log" versions 3 size 5m suffix_increment'

         - name: 'channel server_spam_channel'
           options:

             - name: 'file'
               value: '"/var/log/bind/named_recent_server.log" versions 3 size 5m suffix_increment'

         - name: 'category client'
           options:

             - name: 'channel-1'
               raw: 'client_spam_channel;'

         ...

This will create two log files in :file:`/var/log/bind/` named
:file:`named_recent_client.log` and :file:`named_recent_server.log`,
respectively. If the files reach 5 Mb in size, they'll be rotated, and
a maximum of three log files will be kept. This means that issues with
remote clients/servers can still be found and analyzed if necessary.
