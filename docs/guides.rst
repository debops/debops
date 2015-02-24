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

While project is "at rest", secrets are encrypted inside EncFS directory, and
they don't show up in the ``secret/`` directory. When you use ``debops`` script to
run the playbook, ``padlock`` script unlocks the encrypted directory and secrets
are available again in ``secret/`` directory for ``ansible-playbook`` to use.


How to use LDAP variables
-------------------------

Ansible modules ``ldap_attr`` and ``ldap_entry`` require admin privileges on
LDAP server to create or change entries. To do that, in each task that uses
these modules users need to provide bind DN and password to a privileged
account on LDAP server, which most likely will be delegated as well, since most
of the time LDAP server is configured on a separate host.

To use these 3 variables conveniently in different Ansible roles and playbooks,
a set of ``secret_ldap_*`` variables can be used with the ``ldap_attr`` and
``ldap_entry`` tasks to point Ansible to a correct LDAP server with admin
credentials. Some example uses::

    - name: Create an entry in LDAP database
      ldap_entry:
        dn: 'ou=People,dc=example,dc=org'
        objectClass: [ 'organizationalUnit', 'top' ]
        state: 'present'
        bind_dn: '{{ secret_ldap_admin_bind_dn }}'
        bind_pw: '{{ secret_ldap_admin_bind_pw }}'
      delegate_to: '{{ secret_ldap_server }}'

    - name: Add attribute to an LDAP entry
      ldap_attr:
        dn: 'cn=user,ou=People,dc=example,dc=org'
        name: '{{ item.key }}'
        values: '{{ item.value }}'
        state: 'exact'
        bind_dn: '{{ secret_ldap_admin_bind_dn }}'
        bind_pw: '{{ secret_ldap_admin_bind_pw }}'
      delegate_to: '{{ secret_ldap_server }}'
      with_dict:
        uid: '{{ user_username }}'
        userPassword: '{{ user_password }}'
      no_log: True

Of course for this to work, ``debops.secret`` needs to be included in the
playbook, either as a role, or a role dependency. You can change the values of
``secret_ldap_*`` variables in inventory as you need.

If you use ``debops.slapd`` role to configure an LDAP server, it will
automatically copy the admin accout password to a location defined in
``secret_ldap_admin_password`` variable to be accessed by the ``debops.secret``
role as needed.

