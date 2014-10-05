|DebOps| users
##############

.. |DebOps| image:: http://debops.org/images/debops-small.png
   :target: http://debops.org

|Travis CI| |test-suite| |Ansible Galaxy|

.. |Travis CI| image:: http://img.shields.io/travis/debops/ansible-users.svg?style=flat
   :target: http://travis-ci.org/debops/ansible-users

.. |test-suite| image:: http://img.shields.io/badge/test--suite-ansible--users-blue.svg?style=flat
   :target: https://github.com/debops/test-suite/tree/master/ansible-users/

.. |Ansible Galaxy| image:: http://img.shields.io/badge/galaxy-debops.users-660198.svg?style=flat
   :target: https://galaxy.ansible.com/list#/roles/1605



This role can be used to manage user accounts (and user groups). You can
manage almost all aspects of the users' account, like UID/GID, home
directory, shell, etc. Accounts are configured using lists in Ansible
inventory, with separate lists for:

* admin accounts;
* global list of users created on each host in a cluster;
* list of users created on a group of hosts;
* list of users created on a specific host;

``debops.users`` is meant as a simple way to create a few dozen accounts max,
for larger number of accounts its preferred to use a dedicated solution,
like an LDAP directory.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

::

    ansible-galaxy install debops.users

Are you using this as a standalone role without DebOps?
=======================================================

You may need to include missing roles from the `DebOps common playbook`_
into your playbook.

`Try DebOps now`_ for a complete solution to run your Debian-based infrastructure.

.. _DebOps common playbook: https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml
.. _Try DebOps now: https://github.com/debops/debops/




Role variables
~~~~~~~~~~~~~~

List of default variables available in the inventory:

::

    ---
    
    # Should Ansible manage user accounts? Set to False to disable
    users: True
    
    
    # --- Lists of different accounts to create/manage ---
    
    # root user, if you want to change something on the root account
    users_root:
      - name: 'root'
    
    # Default user created by Ansible
    users_default:
      - name: '{{ ansible_ssh_user }}'
    
    # Administrators
    users_admins: []
    
    # Groups (normal or system)
    users_groups: []
    
    # "Global" users
    users_list: []
    
    # "Host group" users
    users_group_list: []
    
    # "Host" users
    users_host_list: []
    
    
    # --- An example account entry, everything except 'name' is optional
    # List of all recognized values, default value listed first
    #
    #  - name: 'username'               # mandatory, default group if not defined
    #    state: 'present,absent'
    #    group: 'name'                  # default group
    #    groups: []                     # list of groups to set
    #    append: yes/no                 # add to, or set groups
    #    gid: 1000
    #    uid: 1000
    #    shell: '/bin/sh'
    #    comment: 'GECOS entry'
    #    systemuser: False/True         # create system user
    #    systemgroup: False/True        # create system group
    #
    #    dotfiles: False/True           # download and configure dotfiles?
    #    dotfiles_repo: 'repository'
    #    dotfiles_command: 'make all'
    #    dotfiles_creates '~/.zshrc'
    #
    #    # Create ~/.forward file (set to False to remove ~/.forward)
    #    forward: [ 'user@domain', 'account' ]
    #
    #    # Add or disable ssh authorized keys (set to False to remove ~/.ssh/authorized_keys
    #    sshkeys: [ 'list', 'of', 'keys' ]
    
    
    # --- Global defaults ---
    
    # Default shell used for new accounts
    users_default_shell: '/bin/bash'
    
    # List of default groups added to new accounts
    users_default_groups_list: []
    
    # Should default groups be added to existing groups, or replace existing
    # groups?
    users_default_groups_append: 'yes'
    
    # Path to directory where home directories for new users are created
    users_default_home_prefix: '/home'
    
    # Default state of dotfiles on all accounts managed by Ansible
    # False - dotfiles are not configured by default
    # True - dotfiles will be configured by default
    users_default_dotfiles: False
    
    # Default dotfile hash to use
    users_default_dotfiles_key: 'drybjed'
    
    # List of dotfile hashes
    users_dotfiles:
      drybjed:
        repo: 'https://github.com/drybjed/dotfiles.git'
        command: 'make install'
        creates: '~/.zshrc'




Authors and license
~~~~~~~~~~~~~~~~~~~

``users`` role was written by:

- Maciej Delmanowski | `e-mail <mailto:drybjed@gmail.com>`_ | `Twitter <https://twitter.com/drybjed>`_ | `GitHub <https://github.com/drybjed>`_

License: `GPLv3 <https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29>`_

****

This role is part of the `DebOps`_ project. README generated by `ansigenome`_.

.. _DebOps: http://debops.org/
.. _Ansigenome: https://github.com/nickjj/ansigenome/
