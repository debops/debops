.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. Based on the Roundcube docs which are:
.. Copyright (C) 2016-2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. SPDX-License-Identifier: GPL-3.0-only

.. _imapproxy__ref_getting_started:

Getting started
===============

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:

.. _imapproxy__ref_default_setup:

Default setup
-------------

If you don't specify any configuration values, the role will attempt
to automatically detect which IMAP server to connect to
and listen for incoming connections on ``localhost``, port ``1143``.

The defaults are based on the assumption that imapproxy will be installed
on the same host as the service using imapproxy. If you want to proxy
incoming connections from an external host, this can be controlled via the
:envvar:`imapproxy__listen_address` and :envvar:`imapproxy__listen_port`
variables. Note that external access also needs to be allowed using
the firewall variables (:envvar:`imapproxy__allow`,
:envvar:`imapproxy__host_allow` and :envvar:`imapproxy__group_allow`)
if you are using the :ref:`Ferm <debops.ferm>` firewall.

If you want to manually define the server to proxy connections to,
use the :envvar:`imapproxy__imap_fqdn` and :envvar:`imapproxy__imap_port`
variables.


.. _imapproxy__ref_ssl_support:

SSL support
-----------

While imapproxy supports TLS out of the box (using values from the
:ref:`debops.pki` role, if enabled), it does **not** have native
support for SSL.

The recommended setup is either to run imapproxy on the same host
as the IMAP server (meaning that TLS/SSL is not necessary as no
proxy <-> IMAP traffic is sent over the network) or to setup the
IMAP server to allow TLS traffic using explicit TLS.

If you are trying to proxy to an IMAP server that is only available using
IMAPS (usually port ``993``), manual configuration will be necessary.
The authors of imapproxy suggest setting up a SSL tunnel (e.g. using
:ref:`stunnel <debops.stunnel>`).

See :file:`/usr/share/doc/imapproxy/README.ssl` in the imapproxy
package for more details.


.. _imapproxy__ref_srv_records:

IMAP server detection
---------------------

The role first checks if :ref:`debops.dovecot` is installed on the same host
by using local Ansible facts. If so, the local IMAP server will be used.

In the alternative, the role detects the preferred IMAP server by using
:ref:`dns_configuration_srv` for the following services:

.. code-block:: none

   _imap._tcp.{{ imapproxy__domain }} (default port 143)
   _imaps._tcp.{{ imapproxy__domain }} (default port 993)

At the moment only a single SRV resource record is supported by the role.

Finally, the role will fall back to using static domain names for the
respective services, based on the host domain (:envvar:`imapproxy__domain`):

.. code-block:: none

   IMAP:  imap.example.org:143

This allows for deployment of the proxy on a separate host or VM.


.. _imapproxy__ref_example_inventory:

Example inventory
-----------------

To install and configure imapproxy on a host, it needs to be present in the
``[debops_service_imapproxy]`` Ansible inventory group. You may want to
use the role on the same host that is also providing the
:ref:`Dovecot <debops.dovecot>` and webmail (e.g.
:ref:`Roundcube <debops.roundcube>`) services.

.. code-block:: none

   [debops_all_hosts]
   webmail

   [debops_service_dovecot]
   webmail

   [debops_service_imapproxy]
   webmail


.. _imapproxy__ref_example_playbook:

Example playbook
----------------

The following playbook can be used with DebOps. If you are using these role
without DebOps you might need to adapt them to make them work in your setup.

.. literalinclude:: ../../../../ansible/playbooks/service/imapproxy.yml
   :language: yaml
   :lines: 1,5-

This playbook is also shipped with DebOps at
:file:`ansible/playbooks/service/imapproxy.yml`.


.. _imapproxy__ref_ansible_tags:

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::imapproxy``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::imapproxy:pkgs``
  Run tasks related to system package installation.

``role::imapproxy:config``
  Run tasks related to the imapproxy configuration.
