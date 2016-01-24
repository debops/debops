Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To setup ownCloud on a given remote host, it needs to be added to
``[debops_service_owncloud]`` Ansible inventory group:

.. code-block:: none

    [debops_service_owncloud]
    hostname

Additionally it is recommended that you install a database server. You can
install one on the same host as ownCloud or choose a different host:

.. code-block:: none

    [debops_service_mariadb_server]
    hostname

In case you chose a different host, you will need to specify which of your
database servers the ownCloud instance should use by specifying the database
server host as ``owncloud_database_server``.

Example playbook
----------------

Here's an example playbook that can be used to manage ownCloud::

    ---
    - name: Manage MariaDB server
      hosts: debops_service_mariadb_server
      become: True

      roles:

        - role: debops.mariadb_server
          tags: [ 'role::mariadb_server' ]

    - hosts: debops_service_owncloud
      become: True

      roles:

        - role: debops.mariadb
          tags: [ 'role::mariadb' ]
          mariadb_users:
            - database: '{{ owncloud_database_map[owncloud_database].dbname }}'
              user: '{{ owncloud_database_map[owncloud_database].dbuser }}'
              password: '{{ owncloud_database_map[owncloud_database].dbpass }}'
          when: (owncloud_database == 'mariadb')

        - role: debops.postgresql
          postgresql_roles:
            - name: '{{ owncloud_database_name }}' # Separate role is needed when owncloud_database_name != owncloud_database_user
            - name: '{{ owncloud_database_user }}' # Password is not passed directly - it will be read for the file
          postgresql_groups:
            - roles: [ '{{ owncloud_database_user }}' ]
              groups: [ '{{ owncloud_database_name }}' ]
              database: '{{ owncloud_database_name }}'
              enabled: '{{ owncloud_database_name != owncloud_database_user }}'
          postgresql_databases:
            - name: '{{ owncloud_database_name }}'
              owner: '{{ owncloud_database_user }}'
          when: (owncloud_database == 'postgresql')
          tags: [ 'role::postgresql' ]

        - role: debops.php5
          tags: [ 'role::php5' ]
          php5_pools:
            - '{{ owncloud_php5_pool }}'

        - role: debops.apt_preferences
          tags: [ 'role::apt_preferences' ]
          apt_preferences_dependent_list:
            - '{{ nginx_apt_preferences_dependent_list }}'

        - role: debops.ferm
          tags: [ 'role::ferm' ]
          ferm_dependent_rules:
            - '{{ nginx_ferm_dependent_rules }}'

        - role: debops.nginx
          tags: [ 'role::nginx' ]
          nginx_servers:
            - '{{ owncloud_nginx_server }}'
          nginx_upstreams:
            - '{{ owncloud_nginx_upstream_php5 }}'

        - role: debops.owncloud
          tags: [ 'role::owncloud' ]


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::owncloud``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::owncloud:base_install``
  Run tasks related to the installation the ownCloud packages.

``role::owncloud:configure``
  Run tasks related to ownCloud configuration and setup.

``role::owncloud:mail``
  Run tasks related to the deployment of the mail configuration.

``role::owncloud:custom_config``
  Run tasks related to the deployment of the custom configuration.

``role::owncloud:occ``
  Run tasks related to the :command:`occ`.

``role::owncloud:ldap``
  Run tasks related to the LDAP configuration.
