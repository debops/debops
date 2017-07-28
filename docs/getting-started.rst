Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:
   :depth: 1

Default DKIM configuration
--------------------------

The role by default will create a DomainKey for the host's DNS domain, which
will use a ``mail`` DKIM selector. The private key can be found in the
:file:`secret/opendkim/domainkeys/` directory on the Ansible Controller (as
well as on the remote hosts). Using the installed script in the
`secret/opendkim/lib/` directory you can extract the public key in the form of
a DNS TXT record and place it in your DNS zone.

OpenDKIM will be configured to sign mail messages from ``localhost`` and the
host's FQDN. Messages sent from the host's own DNS domain, as well as any
messages from the subdomains will be signed by default.


Support for Unbound DNS resolver
--------------------------------

The ``debops.opendkim`` role checks if the Unbound service has been installed
on a given host, by checking for the Ansible local facts defined by the
``debops.unbound`` role. If Unbound is present, OpenDKIM will automatically use
it to resolve DNS queries and check DNSSEC validity.


Example inventory
-----------------

The install and configure OpenDKIM on a host, it needs to be present in the
``[debops_service_opendkim]`` Ansible inventory group:

.. code-block:: none

   [debops_service_opendkim]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.opendkim`` role:

.. literalinclude:: playbooks/opendkim.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::opendkim``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
