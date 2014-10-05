|DebOps| gitlab
###############

.. |DebOps| image:: http://debops.org/images/debops-small.png
   :target: http://debops.org

|Travis CI| |test-suite| |Ansible Galaxy|

.. |Travis CI| image:: http://img.shields.io/travis/debops/ansible-gitlab.svg?style=flat
   :target: http://travis-ci.org/debops/ansible-gitlab

.. |test-suite| image:: http://img.shields.io/badge/test--suite-ansible--gitlab-blue.svg?style=flat
   :target: https://github.com/debops/test-suite/tree/master/ansible-gitlab/

.. |Ansible Galaxy| image:: http://img.shields.io/badge/galaxy-debops.gitlab-660198.svg?style=flat
   :target: https://galaxy.ansible.com/list#/roles/1566



This role installs `GitLab`_, an Open Source `GitHub`_ clone.
``debops.gitlab`` role will also automatically update installed GitLab
instance if new patches are pushed to the repository.

You can also use this role to upgrade an already installed GitLab instance
to new version when support for it becomes available (new GitLab version is
released on 22nd of each month, usually ``debops.gitlab`` role is updated
to support new version shortly after that).

Default credentials: ``root:5iveL!fe``

.. GitLab: https://about.gitlab.com/
.. GitHub: https://github.com/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

::

    ansible-galaxy install debops.gitlab

Are you using this as a standalone role without DebOps?
=======================================================

You may need to include missing roles from the `DebOps common playbook`_
into your playbook.

`Try DebOps now`_ for a complete solution to run your Debian-based infrastructure.

.. _DebOps common playbook: https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml
.. _Try DebOps now: https://github.com/debops/debops/


Role dependencies
~~~~~~~~~~~~~~~~~

- ``debops.etc_services``- ``debops.redis``- ``debops.nginx``- ``debops.mysql``- ``debops.ruby``- ``debops.secret``- ``debops.postgresql``

Role variables
~~~~~~~~~~~~~~

List of default variables available in the inventory:

::

    ---
    
    # ---- Basic options ----
    
    # Should GitLab role manage it's own dependencies (database, web server)?
    gitlab_dependencies: True
    
    # What version of GitLab to install / manage
    gitlab_version: '7.1'
    
    # Allow automatic upgrades to next version? If not, Ansible will stop execution
    # when it detects that GitLab requires upgrade
    gitlab_auto_upgrade: True
    
    
    # ---- GitLab instance configuration ----
    
    # What database to use for GitLab instnce? Choices: mysql, postgresql
    # Currently only MySQl is supported
    gitlab_database: 'mysql'
    
    # Domain which will be used for nginx server and gitlab-shell access
    # GitLab will be configured with HTTPS enabled by default
    gitlab_domain: [ 'code.{{ ansible_domain }}' ]
    
    # E-mail sender name used by GitLab
    gitlab_email_name: 'GitLab'
    
    # E-mail address used by GitLab
    gitlab_email_from: 'git@{{ gitlab_domain[0] }}'
    
    # E-mail address for GitLab support
    gitlab_email_support: 'root@{{ ansible_domain }}'
    
    
    # ---- New user configuration ----
    
    # Enable sign up on the front page?
    gitlab_signup_enabled: 'true'
    
    # Default project limit for new users
    gitlab_default_projects_limit: '50'
    
    # Should new users be able to create groups?
    gitlab_default_can_create_group: 'true'
    
    # Can users change their own username?
    gitlab_username_changing_enabled: 'false'
    
    # Default GitLab theme to use
    gitlab_default_theme: '2'
    
    
    # ---- Custom redis configuration ----
    
    # Connection string used in the configuration file
    gitlab_redis: 'redis://{{ gitlab_redis_host + ":" + gitlab_redis_port }}'
    
    # Define hostname of redis server to use
    gitlab_redis_host: 'localhost'
    
    # Define port of redis server to use
    gitlab_redis_port: '6379'
    
    
    # ---- Internal application settings ----
    
    # Connection type for PostgreSQL database (choices: socket, port)
    gitlab_postgresql_database_connection: 'socket'
    
    # nginx client_max_body_size value
    gitlab_nginx_client_max_body_size: '5m'
    
    # nginx - gitlab proxy timeout in seconds
    gitlab_nginx_proxy_timeout: '300'
    
    # Max git upload size in bytes
    gitlab_git_max_size: '5242880'
    
    # git connection timeout in seconds
    gitlab_git_timeout: '10'
    
    # unicorn connection timeout in seconds
    gitlab_unicorn_timeout: '30'

List of internal variables used by the role:

::

    gitlab_status_ce_upgrade
    gitlab_status_shell_upgrade
    gitlab_status_shell_installed
    gitlab_postgresql_database_password
    gitlab_status_ce_installed
    gitlab_database_password


Authors and license
~~~~~~~~~~~~~~~~~~~

``gitlab`` role was written by:

- Maciej Delmanowski | `e-mail <mailto:drybjed@gmail.com>`_ | `Twitter <https://twitter.com/drybjed>`_ | `GitHub <https://github.com/drybjed>`_

License: `GPLv3 <https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29>`_

****

This role is part of the `DebOps`_ project. README generated by `ansigenome`_.

.. _DebOps: http://debops.org/
.. _Ansigenome: https://github.com/nickjj/ansigenome/
