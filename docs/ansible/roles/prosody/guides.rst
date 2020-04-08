.. Copyright (C) 2014-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _prosody__ref_guides:

Prosody configuration guides
============================

Here you can find a few guides that can help you configure more advanced
Prosody features.
For more details see the configuration specific to ``prosody`` role.

You can use the `XMPP Compliance Tester <https://compliance.conversations.im/>`_
to check if your server fullfills the suggested compliance settings.

.. _prosody__ref_guides_working_example:

Prosody XMPP Server with multiple Virtual Hosts and Components
--------------------------------------------------------------

This is a real world™ working example of a prosody XMPP server with two
virtual host domains, the corresponding MUC and HTTP_UPLOAD components and
PKI realms.


.. code-block:: yaml
   :caption: ansible/inventory/host_vars/prosody.example.net/pki.yml
   :name: ansible/inventory/host_vars/prosody.example.net/pki.yml

   ---

   pki_host_realms:
     # XMPP Server (Prosody)
     - name: 'xmpp.example.net'
       acme: true
       acme_domains:
         # the virtual host domain
         - 'example.net'
         # the prosody server domain
         - 'xmpp.example.net'
         # the muc domain
         - 'conference.example.net'
         # the upload file service domain
         - 'upload.example.net'

     # Another XMPP Virtual Host
     - name: 'chat.another-domain.com'
       acme: true
       acme_domains:
         # the virtual host domain
         - 'another-domain.com'
         # the prosody server domain
         - 'chat.another-domain.com'
         # the muc domain
         - 'conference.another-domain.com'

.. code-block:: yaml
   :caption: ansible/inventory/host_vars/prosody.example.net/prosody.yml
   :name: ansible/inventory/host_vars/prosody.example.net/prosody.yml

   ---

   prosody__domain: 'example.net'
   prosody__pki_realm: 'xmpp.{{ prosody__domain }}'
   prosody__authentication: 'internal_hashed'
   prosody__admins:
     - 'alice@{{ prosody__domain }}'
   prosody__host_config_global:
     archive_expires_after: '4w'

   prosody__host_virtual_hosts:
     'example.net':
       enabled: true
       pki_realm: 'xmpp.{{ prosody__domain }}'

     'another-domain.com':
       enabled: true
       pki_realm: 'chat.another-domain.com'
       modules_disabled:
         - 'carbons'

   prosody__components:
     'upload.example.net':
       enabled: false
       plugin_name: 'http_upload'

     'conference.another-domain.com':
       enabled: true
       plugin_name: 'muc'
     'upload.another-domain.com':
       enabled: true
       plugin_name: 'http_upload'

   prosody__modules_default:
     - "roster"
     - "saslauth"
     - "tls"
     - "dialback"
     - "disco"
     - "private"
     - "vcard"
     - "blocklist"
     - "version"
     - "uptime"
     - "time"
     - "ping"
     - "pep"
     - "admin_adhoc"
     - "posix"
     - "groups"
     - "carbons"
     - "mam"
     - "blocking"
     - "smacks"
