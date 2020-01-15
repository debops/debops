Getting started
===============

.. contents::
   :local:


Correct DNS configuration is recommended
----------------------------------------

The ``debops.nullmailer`` role uses the ``ansible_fqdn`` and ``ansible_domain``
variables to create correct values for the ``nullmailer`` service. It's
recommended that the hosts which use ``nullmailer`` have the proper DNS
configuration, which means that they should be resolvable in the DNS by their
Fully Qualified Domain Name (hostname + domain name). The FQDN doesn't need to
be accessible from the Internet when the hosts are on a private network, but
it's recommended to select a subdomain of your main DNS domain and configure
the DNS servers to advertise it on your private subnets.


No local mail by default
------------------------

The ``nullmailer`` service does not provide support for local mail - all mail
is forwarded to the configured SMTP servers for further processing. If you need
more advanced SMTP configuration, you should check out the :ref:`debops.postfix`
role which can configure the Postfix MTA. This also means that in a new
environment, you should prepare at least 1 host as the central mail hub for
your network, or use an already existing SMTP server for relaying mail
messages.

The ``debops.nullmailer`` role is designed to allow automatic switch to
a different SMTP server - if it detects a ``postfix`` package installed on
a host, it will automatically disable configuration of the ``nullmailer``
service to not interfere with existing Postfix configuration.

All mail directed to the local recipients will be forwarded to the ``root``
UNIX account on the upstream SMTP mail relay - if it's Postfix, then this will
be a local UNIX account. There you can deal with the e-mail messages as you see
fit - forward them to a virtual ``root@<domain>`` account, or to other people,
filter them, etc.

Local sender and recipient addresses without specified FQDN domain will have
the host's FQDN set in their e-mail address "domain" part. This might be not
desirable when you use multiple hosts behind a mail relay and send messages to
external recipients. In that case, in the Postfix service on the mail relay you
can configure `domain masquerading`__ to mask the internal hostnames.

.. __: http://www.postfix.org/ADDRESS_REWRITING_README.html#masquerade

If you use the :ref:`debops.postfix` role to manage the mail relay, you can do
that with the following configuration in the Ansible inventory:

.. code-block:: yaml

   postfix__maincf:

     - name: 'masquerade_domains'
       value: [ 'example.org' ]

     - name: 'local_header_rewrite_clients'
       value: [ 'permit_inet_interfaces, 'permit_mynetworks',
                'permit_sasl_authenticated' ]

     - name: 'masquerade_exceptions'
       value: [ 'MAILER-DAEMON', 'postmaster', 'root' ]

This will mask ``any.thing.example.org`` in the e-mail addresses of senders and
recipients and will convert them to ``example.org``. The exceptions will ensure
that the mail from ``root`` account is not rewritten and points to the correct
host.


Default SMTP relay
------------------

The upstream SMTP relay is configured in the :envvar:`nullmailer__relayhost`
variable. The role by default will check the DNS SRV resource records of the
host's DNS domain to find the preferred SMTP server. You can define these
records in the DNS:

.. code-block:: none

   _smtp._tcp     SRV   0 1 25   smtp.example.org.

Only a single SRV record is supported, with multiple records only one will be
selected based on the alphabetical order. If the SRV records are not found, the
role will fall back to using the ``smtp`` subdomain.

To set the desired value for all hosts in your environment, set in the
inventory:

.. code-block:: yaml

   # ansible/inventory/group_vars/all/nullmailer.yml

   nullmailer__relayhost: '<FQDN address of mail server>'


LDAP integration
----------------

If the :ref:`LDAP environment <debops.ldap>` is configured on the host, the
:ref:`debops.nullmailer` role will automatically use it to create an LDAP
service account in the directory. The relayhost configuration will have SMTP
authentication enabled with the ``nullmailer@<host.example.org>`` username,
which can then be used by the relay server via SASL authentication to find the
corresponding ``nullmailer`` account in the LDAP directory and authenticate the
service.

See the :ref:`debops.postldap` Ansible role documentation for details about
configuring Postfix mail relay with LDAP directory support.


Example inventory
-----------------

The ``debops.nullmailer`` role is included by default in the ``common`` DebOps
playbook and you don't need to add a host to a custom inventory group to
activate it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nullmailer`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nullmailer.yml
   :language: yaml
