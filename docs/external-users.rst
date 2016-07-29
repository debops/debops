.. _owncloud__ref_external_users:

External users
==============

.. include:: includes/all.rst

This section gives more details on how to setup external users for ownCloud.

Users from debops.slapd
-----------------------

Should work out of the box when enabled:

.. code-block:: yaml

   owncloud__ldap_enabled: True

Users from MS Windows Active Directory
--------------------------------------

First, you will need an AD user with which ownCloud can do a LDAP bind in order
to read information about the users and check passwords.
This user should be unprivileged.

Create the AD user and configure it like this:

::

    [ ] User must change password at next logon
    [x] User cannot change password
    [x] Password never expires
    [ ] Account is disabled

The user must not be able to login from computers.
FIXME: Figure out how that can be configured.


.. code-block:: yaml

   owncloud__ldap_enabled: True

   # ownCloud LDAP recommendations by the debops.owncloud maintainers for MS Windows AD [[[
   # Note that those recommendations might deviate from ownCloud
   # recommendations but those are the settings which are proven to work.
   owncloud__ldap_create_user: False
   owncloud__ldap_port: '389'
   owncloud__ldap_expert_username_attr: 'sAMAccountName'

   owncloud__ldap_conf_map:
     ldapHost: '{{ "ldaps://" if (owncloud__ldap_method == "ssl") else "" }}{{ owncloud__ldap_host }}'
     ldapPort: '{{ owncloud__ldap_port }}'
     ldapAgentName: '{{ owncloud__ldap_binddn }}'
     ldapBase: '{{ owncloud__ldap_basedn }}'
     ldapExpertUsernameAttr: '{{ owncloud__ldap_expert_username_attr }}'
   # .. ]]]

   # Custom settings.
   owncloud__ldap_host: 'dc01.example.org'
   owncloud__ldap_basedn: 'DC=example,DC=org'
   owncloud__ldap_binddn: 'CN=owncloudbind,OU=service-users,{{ owncloud__ldap_basedn }}'

Refer to debops.secret_ to learn how passwords are handled.
