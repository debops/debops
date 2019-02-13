Detailed guides
===============

How local secrets work
----------------------

Here's a default project directory layout kept in a git repository:

.. code-block:: none

   ~/Projects/
   `-- data-center/
       |-- .git/
       `-- ansible/
           |-- inventory/
           |   |-- group_vars/
           |   |-- host_vars/
           |   `-- hosts
           |
           `-- secret/
               |-- credentials/
               `-- storage/

If you use the :command:`debops-padlock` script to create encrypted EncFS
storage for your secrets, directory layout will be slightly different:

.. code-block:: none

   ~/Projects/
   `-- data-center/
       |-- .git/
       `-- ansible/
           |-- .encfs.secret/        <- encrypted secrets
           |   |-- U8dfMgfgg48vj/
           |   |-- fk5fkg5NN/
           |   `-- padlock*          <- unlock/lock script
           |
           |-- inventory/
           |   |-- group_vars/
           |   |-- host_vars/
           |   `-- hosts
           |
           `-- secret/               <- plaintext secrets

While the project is "at rest", secrets are encrypted inside EncFS directory,
and they don't show up in the :file:`secret/` directory. When you use the
:command:`debops` script to run the playbook, the :command:`padlock` script
unlocks the encrypted directory and secrets are available again in the
:file:`secret/` directory for :command:`ansible-playbook` to use.


How to use LDAP variables
-------------------------

DebOps relies on the ``ldap_attr`` and ``ldap_entry`` Ansible modules to
perform LDAP management on local or remote LDAP servers. In various DebOps
roles, they are used to perform certain tasks in a shared environment.

Some of the above tasks require admin privileges on the LDAP server. To provide
access to it in a secure manner, ``debops.secret`` role keeps a set of
variables meant to be used with these tasks.

For security reasons, LDAP-related tasks should be delegated to ``localhost``
(Ansible Controller) or the LDAP server itself. The host that runs these tasks
requires ``python-ldap`` library. Modules will access LDAP directly, without
using SSH redirection, so TLS encryption is strongly recommended. You should
also take care to not log these tasks to avoid leaking the LDAP administrator
password in logs.

Example usage of LDAP secret variables:

.. code-block:: yaml

   - name: Create an entry in LDAP database
     ldap_entry:
       dn:          '{{ secret__ldap_ou_people_dn }}'
       objectClass: [ 'organizationalUnit', 'top' ]
       state:       'present'
       server_uri:  '{{ secret__ldap_server_uri }}'
       start_tls:   '{{ secret__ldap_start_tls }}'
       bind_dn:     '{{ secret__ldap_bind_dn }}'
       bind_pw:     '{{ secret__ldap_bind_pw }}'
     become:        '{{ secret__ldap_become }}'
     delegate_to:   '{{ secret__ldap_delegate_to }}'
     no_log: '{{ secret__no_log | bool }}'

   - name: Add attribute to an LDAP entry
     ldap_attr:
       dn:         'uid=user,{{ secret__ldap_ou_people_dn }}'
       name:       '{{ item.key }}'
       values:     '{{ item.value }}'
       state:      'exact'
       server_uri: '{{ secret__ldap_server_uri }}'
       start_tls:  '{{ secret__ldap_start_tls }}'
       bind_dn:    '{{ secret__ldap_bind_dn }}'
       bind_pw:    '{{ secret__ldap_bind_pw }}'
     become:       '{{ secret__ldap_become }}'
     delegate_to:  '{{ secret__ldap_delegate_to }}'
     with_dict:
       uid:          '{{ user_username }}'
       userPassword: '{{ user_password }}'
     no_log: '{{ secret__no_log | bool }}'

Of course for this to work, ``debops.secret`` needs to be included in the
playbook, either as a role, or a role dependency. You can change the values of
``secret__ldap_*`` variables in inventory as you need.

If you use ``debops.slapd`` role to configure an LDAP server, it will
automatically copy the admin account password to a location defined in
``secret__ldap_admin_password`` variable to be accessed by the ``debops.secret``
role as needed.
