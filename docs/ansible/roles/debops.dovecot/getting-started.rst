Getting started
===============

.. contents::
   :local:

Default setup
-------------

If you don't specify any configuration values, the role will setup an IMAP and IMAPS
service using the certificates provided by `ansible-pki`_. It will further use the
`ansible-ferm`_ role to open the required network ports with iptables: 143 (IMAP+STARTTLS)
and 993 (IMAPS). Every user account which is able to login via PAM, can then also
login via IMAP and access its mails stored as an mbox file in ``/var/mail/<username>``.

Example inventory
-----------------

You can install Dovecot on a host by adding it to the ``[debops_service_dovecot]`` group
in your Ansible inventory::

    [debops_service_dovecot]
    hostname

Example playbook
----------------

Here's an example playbook which uses ``debops.dovecot`` role to install Dovecot:

.. literalinclude:: ../../../../ansible/playbooks/service/dovecot.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::dovecot``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

.. _ansible-pki: https://github.com/debops/ansible-pki
.. _ansible-ferm: https://github.com/debops/ansible-ferm

