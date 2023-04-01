.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _bind__ref_keys:

Keys
====

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:


.. _bind_ref_keys_intro:

Introduction
------------

The ``bind__*_keys`` variables control the generation of keys on the BIND
server.  The keys which are generated on the server can be transferred to the
Ansible Controller and be used to authenticate clients which wish to perform
dynamic DNS updates or to distinguish operations, including queries, which are
to be performed on different views.

.. note::
   Keys control client access to the server, and are not related to DNSSEC
   keys.

Generated keys are stored on the server in the :file:`/etc/bind/keys/`
directory and on the controller in the
:file:`secret/bind/<ansible_inventory_name>` directory (see
:ref:`debops.secret` for details).

.. _bind__ref_keys_types:

Key Types
---------

BIND supports two different kinds of key types, ``TSIG`` and ``SIG(0)`` keys.

TSIG keys are symmetric keys, meaning that the BIND server and the client
each need a copy of the same key. SIG(0) keys are asymmetric keys, meaning
that there is a public key (known to the server) and a private key
(known to the client).

TSIG keys are generally easier to work with, but SIG(0) have the advantage
that they can be updated by the client and that the public key does not
need to be kept secret.

SIG(0) public keys need to be published *in the zone*, which means that the
name used for the key is significant. For example, if you create a key named
``test.example.com``, two files will be generated, which will be named
``Ktest.example.com.+<algorithm><random ID>`` with the suffix ``.private`` and
``.key``. The latter is the *public key*, and its contents will look something
like this:

.. code-block:: console

   # cat Ktest.example.com.+013+05418.key
   test.example.com. IN KEY 512 3 13 dVdLP...xhNNvF7A==

The public key needs to be published in the ``example.com`` zone, e.g. using
:command:`nsupdate` (this example assumes execution on the host running
BIND):

.. code-block:: console

   # cat nsupdate.txt
   server localhost
   zone example.com
   ttl 3600
   add test.example.com. IN KEY 512 3 13 dVdLP...xhNNvF7A==
   send

   # nsupdate < nsupdate.txt

.. _bind__ref_keys_examples:

Examples
--------

Generate two keys which can be used e.g. in ACLs to distinguish between
different views:

.. code-block:: yaml

   bind__keys:

     - name: 'external-key'
       type: 'tsig'
       algorithm: 'hmac-sha512'

     - name: 'internal-key'
       type: 'tsig'
       algorithm: 'hmac-sha512'

See the zones/views :ref:`example<bind__ref_zones_examples_view>` for a full
example making use of these keys.

Generating a SIG(0) key:

.. code-block:: yaml

   bind__keys:

     - name: 'test.example.com.'
       type: 'sig(0)'
       algorithm: 13

.. _bind__ref_keys_syntax:

Syntax
------

The key configuration uses YAML dictionary keys as the configuration option
name. Valid options are:

``name``
  Required. Key name. This is used both as a basis for the filename and also
  to refer to the key in the BIND configuration file.

``state``
  Optional. Can either be ``present`` or ``absent`` (other values mean the key
  will be ignored. Defaults to ``present``. An ``absent`` key will be removed
  from the server.

``type``
  Required. The type of key to generate. Currently ``tsig`` and ``sig(0)``
  are supported.

``algorithm``
  Required. The crypto algorithm to use for the key.

  Possible algorithms for TSIG keys are (see :man:`tsig-keygen`):

  * hmac-md5
  * hmac-sha1
  * hmac-sha224
  * hmac-sha256
  * hmac-sha384
  * hmac-sha512

  Algorithms for SIG(0) keys *must* be numeric (see `this list`__) and the
  possible algorithms are (see :man:`dnssec-keygen`):

  * 5 - RSASHA1
  * 7 - NSEC3RSASHA1
  * 8 - RSASHA256
  * 10 - RSASHA512
  * 13 - ECDSAP256SHA256
  * 14 - ECDSAP384SHA384
  * 15 - ED25519
  * 16 - ED448

  Note that the supported algorithms for both key types can vary with the
  specific release of BIND which is installed.

.. __: https://www.iana.org/assignments/dns-sec-alg-numbers/dns-sec-alg-numbers.xhtml

``dir``
  Optional. The directory on the server in which to store the generated key.
  Default: :file:`/etc/bind/keys/`.

``owner``
  Optional. The user which should own the generated key file(s). Default:
  ``root``.

``group``
  Optional. The group which should own the generated key file(s). Default:
  ``bind``.

``download``
  Optional. Whether the key should be downloaded to the Ansible controller.
  Default: True unless ``source`` is "controller".

``source``
  Optional, string. Either "host" (the default), meaning that the key should
  be generated on the remote host, or "controller", meaning that the key should
  be copied from the Ansible controller to the remote host (in which case,
  ``source_path`` also needs to be set).

``source_path``
  Optional, string. If ``source`` is set to "controller", the path to the
  (public) key on the Ansible controller. A relative path will be interpreted
  as relative to the :ref:`debops.secret` directory. The filename used for the
  key file on the remote host will be the same as on the controller.

``include``
  Optional, boolean. Whether the key should be included in the BIND
  configuration file. This option only makes sense for TSIG keys.
  Default: True.

``remove_private_key``
  Optional, boolean. Whether the private key of an asymmetric key pair
  should be removed from the server. This option only makes sense for
  SIG(0) keys. Default: True.
