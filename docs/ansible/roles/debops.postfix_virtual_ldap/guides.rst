.. _postldap__ref_guides:

Postfix configuration guides
============================

Here you can find a few guides that can help you configure more advanced
Postfix features. Some of these can and are implemented as separate Ansible
roles, here you can see the configuration specific to ``debops.postfix`` role.

.. contents:: Sections
   :local:

.. _postldap__ref_guides_virtual_user_mail:

Configure Postfix as a Virtual User Mail System
-----------------------------------------------

This guide describes how to set up a virtual user mail system, i.e.
where the senders and recipients do not correspond to the Linux system users.

It requires a working LDAP infrastructure (See :ref:`debops.ldap` and
:ref:`debops.slapd`) in order to manage and authenticate the users and get
the corresponding email address and aliases.
It is also possible to configure accounts with `wildcard` (catch-all)
email addresses. The default configuration uses first the aliases set by
:ref:`debops.etc_aliases` and then queries the LDAP server, if no match was found.

See also :ref:`debops.dovecot` and :ref:`debops.roundcube` for an IMAP server
and Email-Webclient correspondingly.

.. code-block:: yaml

  Work in progress...

