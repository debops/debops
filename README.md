
## [![DebOps project](http://debops.org/images/debops-small.png)](http://debops.org) postgresql



[![Travis CI](http://img.shields.io/travis/debops/ansible-postgresql.svg?style=flat)](http://travis-ci.org/debops/ansible-postgresql) [![test-suite](http://img.shields.io/badge/test--suite-ansible--postgresql-blue.svg?style=flat)](https://github.com/debops/test-suite/tree/master/ansible-postgresql/)  [![Ansible Galaxy](http://img.shields.io/badge/galaxy-debops.postgresql-660198.svg?style=flat)](https://galaxy.ansible.com/list#/roles/1590) [![Platforms](http://img.shields.io/badge/platforms-debian%20|%20ubuntu-lightgrey.svg?style=flat)](#)






`debops.postgresql` is an Ansible role which can install and manage
[PostgreSQL](http://postgresql.org/) database servers. It's built around
Debian solution for managing PostgreSQL "clusters" and can manage multiple
clusters and PostgreSQL versions at once.

By default PostgreSQL 9.1 available in Debian Wheezy will be installed, but
you can enable PostgreSQL 9.3 version which will be installed using
official [PostgreSQL Global Development Group)(https://wiki.postgresql.org/wiki/Apt)
repositories.





### Installation

This role requires at least Ansible `v1.7.0`. To install it, run:

    ansible-galaxy install debops.postgresql

#### Are you using this as a standalone role without DebOps?

You may need to include missing roles from the [DebOps common
playbook](https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml)
into your playbook.

[Try DebOps now](https://github.com/debops/debops) for a complete solution to run your Debian-based infrastructure.





### Role dependencies

- `debops.secret`
- `debops.etc_services`
- `debops.ferm`





### Role variables

List of default variables available in the inventory:

    ---
    
    # PostgreSQL version installed by default and used for all PG clusters
    postgresql_version: '9.1'
    
    # Enable PostgreSQL Global Developmet Group APT repository?
    # More information: https://wiki.postgresql.org/wiki/Apt
    postgresql_pgdg: False
    
    # System user and group which managages PostgreSQL clusters
    postgresql_owner: 'postgres'
    postgresql_group: 'postgres'
    
    # List od hosts/networks to allow through firewall. By default nothing is allowed
    #postgresql_default_allow:
    #  - '192.168.0.0/16'
    
    # The default password for the postgres user.
    # This is set for each cluster by default but you can override it for each cluster.
    # Check https://github.com/ginas/ginas/tree/master/playbooks/roles/ginas.secret for more information on how this works.
    postgresql_default_postgres_password: "{{ lookup('password', secret + '/credentials/' + ansible_fqdn + '/postgresql/default/postgres/password length=20') }}"
    
    # Where to log system/error messages
    # Options: stderr, csvlog, syslog, and eventlog
    postgresql_default_log_destination: 'syslog'
    
    # Default localisation settings. Error messages will be printed in English
    # independently of selected PostgreSQL locale. This locale will also be used at
    # cluster creation to set default database encoding
    postgresql_default_locale: 'en_US.UTF-8'
    postgresql_default_locale_messages: 'C'
    
    # Timezone configured in PostgreSQL clusters, by default use timezone settings
    # from Ansible Controller or fallback to UTC
    postgresql_default_timezone: ""
    
    # Where SSL certificates are stored. See 'pki' role
    postgresql_pki_path: '/srv/pki'
    
    # Certificates used for each PostgreSQL cluster if not changed otherwise
    # By default, use self-signed host certificate
    postgresql_default_ssl_root: '{{ postgresql_pki_path }}/host/selfsigned/{{ ansible_fqdn }}.crt'
    postgresql_default_ssl_crl: '{{ postgresql_pki_path }}/host/crl/{{ ansible_fqdn }}.crl'
    postgresql_default_ssl_crt: '{{ postgresql_pki_path }}/host/selfsigned/{{ ansible_fqdn }}.crt'
    postgresql_default_ssl_key: '{{ postgresql_pki_path }}/host/private/{{ ansible_fqdn }}.key'
    postgresql_default_ssl_ciphers: 'ALL:!ADH:!LOW:!EXP:!MD5:@STRENGTH'
    
    # Default startup behaviour: auto, manual, disabled
    postgresql_default_start_conf: 'auto'
    
    # How much % of RAM to use for shared memory?  By default 0.5 means half
    # of system memory will be used for shmmax and shmall calculations
    # http://www.postgresql.org/docs/9.1/static/kernel-resources.html
    # Set to False to disable shared memory changes
    postgresql_sysctl_shm_multiplier: 0.5
    
    # Default maximum number of connections
    postgresql_default_max_connections: '100'
    
    # Default WAL and archivisation settings
    # Options: minimal, archive, hot_standby
    postgresql_default_wal_level: 'minimal'
    postgresql_default_archive_command: ''
    
    # User to cluster mapping. This is a text block which will be pasted "as is"
    # into /etc/postgresql-common/user_clusters
    # By default, nothing is configured
    postgresql_user_clusters: False
    
    # Host based authentication defaults. This is a text block which will be pasted
    # "as is" into pg_hba.conf *after* any hba settings from a particular cluster.
    # Settings for system superuser (postgres) are set in pg_hba.conf template
    postgresql_default_hba: |
      local   all             all                             peer
      host    all             all             127.0.0.1/32    md5
      host    all             all             ::1/128         md5
    
    # User identification defaults. This is a text block which will be pasted "as
    # is" into pg_ident.conf *before* any ident settings from a particular cluster.
    # By default, nothing is configured
    postgresql_default_ident: False
    
    # Lists of PostgreSQL clusters to manage. Each entry should have at least
    # a name and a port on which to bind the cluster. Other options listed below
    # are optional. You can also add all PG parameters from postgresql.conf to
    # a cluster entry
    #
    # To disable one or both lists, set them as empty: '[]'. This will allow for
    # cluster counting task to work correctly (needed to set correct amounts of
    # shared memory for each cluster, divided by number of clusters configured on
    # the host)
    
    # Configuration for default "main" cluster
    postgresql_default_cluster:
    
      - name: 'main'
        port: '5432'
    
        # Parameters below are optional. More parameters can be found in postgresql.conf template
        #user: 'postgres'
        #group: 'postgres'
        #postgres_password: "{{ lookup('password', secret + '/credentials/' + ansible_fqdn + '/postgresql/9.1/main/postgres/password length=20') }}"
        #version: '{{ postgresql_version }}'
        #ssl_root: '{{ postgresql_default_ssl_root }}'
        #ssl_crt: '{{ postgresql_default_ssl_crt }}'
        #ssl_key: '{{ postgresql_default_ssl_key }}'
        #start_conf: 'auto'
        #environment:
        #  VARIABLE: 'value'
        #listen_addresses: 'localhost'
        #hba:
        #  - hosts: [] # example: '{{ groups['apps'] }}'
        #    type: 'host'
        #    interface: 'br2'
        #    user: 'all'
        #    database: '{{ user }}'
        #    auth: 'md5'
        #  - address: '' # example: '192.168.0.0/16
        #ident: |
        #  # Freeform (see postgresql_default_hba)
        #allow:
        #  - '10.0.0.0/8'
        #  - '172.16.0.0/12'
        #  - '192.168.0.0/16'
    
    # Configuration for other clusters
    postgresql_clusters: []
    
    
    # ---- Auto backups ----
    
    # Backups will be ran daily and are rotated weekly.
    # Weekly backups are rotated on a 5 week cycle.
    # Monthly backups are ran on the first of the month.
    # Monthly backups are not rotated.
    #   It would be a good idea to move monthly backups to a remote server yourself.
    
    # Should auto backups be enabled?
    # If set to False, the script will be removed from /etc/cron.daily.
    postgresql_auto_backup: True
    
    # Available options:
    #   - log    : send only the log file
    #   - files  : send the log file and sql files as attachments
    #   - stdout : output the log to the screen if run manually
    #   - quiet : only send logs if an error occurs
    postgresql_auto_backup_mailcontent: 'quiet'
    
    # The maximum allowed size of the e-mail, 4000 = about 5mb.
    postgresql_auto_backup_maxsize: 4000
    
    # Who should receive the backup files?
    postgresql_auto_backup_mailaddr: 'backup@{{ ansible_domain }}'
    
    # Include create database in the backup? Use 'yes' or 'no', not true/false.
    postgresql_auto_backup_create_database: 'yes'
    
    # Use a separate backup directory and file for each database? 'yes' or 'no'.
    postgresql_auto_backup_isolate_databases: 'yes'
    
    # Which day of the week do you want to perform weekly backups?
    # 1 = Monday , ... , 7 = Sunday.
    postgresql_auto_backup_weekly_day: 6
    
    # Should the dumps be encrypted? 'yes' or 'no'
    postgresql_auto_backup_encryption: 'no'
    postgresql_auto_backup_encryption_public_key: ''
    
    # Scripts to execute before and/or after the backup takes place.
    # An empty value disables this feature, provide a path to the script to enable.
    postgresql_auto_backup_pre_script: ''
    postgresql_auto_backup_post_script: ''



List of internal variables used by the role:

    postgresql_cluster_count
    postgresql_default_timezone






### Authors and license

`postgresql` role was written by:

- Maciej Delmanowski | [e-mail](mailto:drybjed@gmail.com) | [Twitter](https://twitter.com/drybjed) | [GitHub](https://github.com/drybjed)

- Nick Janetakis | [e-mail](mailto:nick.janetakis@gmail.com) | [Twitter](https://twitter.com/nickjanetakis) | [GitHub](https://github.com/nickjj)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29)



***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).
