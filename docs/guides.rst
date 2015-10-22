Detailed guides
===============

How local secrets work
----------------------

Here's a default project directory layout kept in a git repository::

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

If you use ``debops-padlock`` script to create encrypted EncFS storage for your
secrets, directory layout will be slightly different::

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

While the project is "at rest", secrets are encrypted inside EncFS directory, and
they don't show up in the ``secret/`` directory. When you use the ``debops`` script to
run the playbook, the ``padlock`` script unlocks the encrypted directory and secrets
are available again in the ``secret/`` directory for ``ansible-playbook`` to use.


How to use LDAP variables
-------------------------

In the `main DebOps playbook repository`_ you can find the Ansible modules
``ldap_attr`` and ``ldap_entry``. They can be used to access and control LDAP
servers. In various DebOps roles, they are used to perform certain tasks in
a shared environment.

Some of the above tasks require admin privileges on the LDAP server. To provide
access to it in a secure manner, ``debops.secret`` role keeps a set of
variables meant to be used with these tasks.

For security reasons, LDAP-related tasks should be delegated to ``localhost``
(Ansible Controller) or the LDAP server itself. The host that runs these tasks
requires ``python-ldap`` library. Modules will access LDAP directly, without
using SSH redirection, so TLS encryption is strongly recommended. You should
also take care to not log these tasks to avoid leaking the LDAP administrator
password in logs.

Example usage of LDAP secret variables::

    - name: Create an entry in LDAP database
      ldap_entry:
        dn: 'ou=People,dc=example,dc=org'
        objectClass: [ 'organizationalUnit', 'top' ]
        state: 'present'
        server_uri: '{{ secret_ldap_server_uri }}'
        start_tls:  '{{ secret_ldap_start_tls }}'
        bind_dn: '{{ secret_ldap_admin_bind_dn }}'
        bind_pw: '{{ secret_ldap_admin_bind_pw }}'
      sudo: '{{ secret_ldap_sudo }}'
      delegate_to: '{{ secret_ldap_delegate_to }}'
      no_log: True

    - name: Add attribute to an LDAP entry
      ldap_attr:
        dn: 'cn=user,ou=People,dc=example,dc=org'
        name: '{{ item.key }}'
        values: '{{ item.value }}'
        state: 'exact'
        server_uri: '{{ secret_ldap_server_uri }}'
        start_tls:  '{{ secret_ldap_start_tls }}'
        bind_dn: '{{ secret_ldap_admin_bind_dn }}'
        bind_pw: '{{ secret_ldap_admin_bind_pw }}'
      sudo: '{{ secret_ldap_sudo }}'
      delegate_to: '{{ secret_ldap_delegate_to }}'
      with_dict:
        uid: '{{ user_username }}'
        userPassword: '{{ user_password }}'
      no_log: True

Of course for this to work, ``debops.secret`` needs to be included in the
playbook, either as a role, or a role dependency. You can change the values of
``secret_ldap_*`` variables in inventory as you need.

If you use `debops.slapd`_ role to configure an LDAP server, it will
automatically copy the admin account password to a location defined in
``secret_ldap_admin_password`` variable to be accessed by the ``debops.secret``
role as needed.

.. _main DebOps playbook repository: https://github.com/debops/debops-playbooks/
.. _debops.slapd: https://github.com/debops/ansible-slapd/

