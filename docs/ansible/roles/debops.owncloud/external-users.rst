.. _owncloud__ref_external_users:

External users
==============

This section gives more details on how to setup external users for ownCloud.

Users from debops.slapd
-----------------------

Should work out of the box when enabled:

.. code-block:: yaml

   owncloud__ldap_enabled: True

Refer to :ref:`owncloud__ref_ldap_defaults` for details.

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
   owncloud__ldap_method: 'plain'
   owncloud__ldap_expert_username_attr: 'sAMAccountName'

   owncloud__ldap_conf_map:
     ldapHost: '{{ owncloud__ldap_primary_server }}'
     ldapPort: '{{ owncloud__ldap_port }}'
     ldapAgentName: '{{ owncloud__ldap_binddn }}'
     ldapBase: '{{ owncloud__ldap_base_dn | join(",") }}'
     ldapExpertUsernameAttr: '{{ owncloud__ldap_expert_username_attr }}'
   # .. ]]]

   # Custom settings.
   owncloud__ldap_primary_server: 'dc01.example.org'
   owncloud__ldap_base_dn: [ 'DC=example', 'DC=org' ]
   owncloud__ldap_binddn: 'CN=owncloudbind,OU=service-users,{{ owncloud__ldap_base_dn | join(",") }}'

Note that this leaves the LDAP configuration in ownCloud at an unfinished state.
The role maintainers consider it to be easier to finish the LDAP configuration
via the admin web interface.
TODO: Add a backup option of all LDAP settings to the Ansible controller.

Refer to :ref:`debops.secret` to learn how passwords are handled.
