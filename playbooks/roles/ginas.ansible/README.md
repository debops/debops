ansible
=======

An Ansible role which builds and installs Debian package with specified Ansible
version (by default, `devel`). It can be used to easily create remote Ansible
Controller host or test your playbooks on a `devel` Ansible version in
a container or VM.

Ansible role will automatically detect installed `redis` service and configure
support for fact caching.

Role Variables
--------------

    # ---- Ansible .deb package build ----
    
    # Ansible version to build
    role_ansible_version: 'devel'
    
    # User which will be used to clone and build Ansible
    # By default, current system user
    role_ansible_build_user: '{{ ansible_ssh_user | default(lookup("env","USER")) }}'
    
    # Where Ansible will be cloned and built, relative to user's $HOME
    role_ansible_build_path: 'src/github.com/ansible/ansible'
    
    # Ansible repository which will be cloned
    role_ansible_git_repository: 'https://github.com/ansible/ansible.git'
    
    
    # ---- /etc/ansible/ansible.cfg ----
    
    # Ansible will use 'inventory/' directory in local directory by default
    role_ansible_config_hostfile: 'inventory/'
    
    # How many forks to use by default
    role_ansible_config_forks: '5'
    
    # How Ansible should gather host facts during playbook execution
    role_ansible_config_gathering: 'smart'
    
    # List of directories to look for Ansible roles
    role_ansible_config_roles_path: [ '/etc/ansible/roles' ]
    
    # Should Ansible check SSH host fingerprint?
    role_ansible_config_host_key_checking: True
    
    # Default module to use if none is specified
    role_ansible_config_default_module_name: 'command'
    
    # Default hash behaviour, 'replace' or 'merge'
    role_ansible_config_hash_behaviour: 'replace'
    
    # 'ansible_managed' contents
    role_ansible_config_ansible_managed: 'Ansible managed: {file} modified on %Y-%m-%d %H:%M:%S by {uid} on {host}'
    
    # Should Ansible display skipped hosts?
    role_ansible_config_display_skipped_hosts: True
    
    # Specify what fact caching mode to use, currently 'memory' or 'redis'. Leave
    # undefined to let Ansible role detect redis by itself
    role_ansible_config_fact_caching: ''
    
    # Timeout for cached host facts, by default 24h
    role_ansible_config_fact_caching_timeout: '{{ (60 * 60 * 24) }}'

Usage examples
--------------

You can use this role in a playbook directly:

    ---
    - hosts: ansible_controller
      sudo: True
      roles:
        - role: ginas.ansible

Or it can be used as a dependency for another role, which for example downloads
and sets up your playbook:

    ---
    dependencies:
      - role: ginas.ansible

License
-------

GPLv3

Author Information
------------------

Maciej Delmanowski <drybjed@gmail.com>

This role is part of the [ginas](https://github.com/ginas/ginas/) project.

