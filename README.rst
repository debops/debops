|DebOps| boxbackup
##################

.. |DebOps| image:: http://debops.org/images/debops-small.png
   :target: http://debops.org

|Travis CI| |test-suite| |Ansible Galaxy|

.. |Travis CI| image:: http://img.shields.io/travis/debops/ansible-boxbackup.svg?style=flat
   :target: http://travis-ci.org/debops/ansible-boxbackup

.. |test-suite| image:: http://img.shields.io/badge/test--suite-ansible--boxbackup-blue.svg?style=flat
   :target: https://github.com/debops/test-suite/tree/master/ansible-boxbackup/

.. |Ansible Galaxy| image:: http://img.shields.io/badge/galaxy-debops.boxbackup-660198.svg?style=flat
   :target: https://galaxy.ansible.com/list#/roles/1555


Warning, this is a BETA role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This role has been marked by the author as a beta role, which means that it
might be significantly changed in the future. Be careful while using this role
in a production environment.

****

`BoxBackup`_ is an automated, centralized, encrypted backup service. This
role will install and configure the server on specified host and then
configure all specified clients to create backup on the
``boxbackup-server`` host.

.. _BoxBackup: http://boxbackup.org/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

::

    ansible-galaxy install debops.boxbackup

Are you using this as a standalone role without DebOps?
=======================================================

You may need to include missing roles from the `DebOps common playbook`_
into your playbook.

`Try DebOps now`_ for a complete solution to run your Debian-based infrastructure.

.. _DebOps common playbook: https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml
.. _Try DebOps now: https://github.com/debops/debops/


Role dependencies
~~~~~~~~~~~~~~~~~

- ``debops.ferm``- ``debops.etc_services``- ``debops.secret``

Role variables
~~~~~~~~~~~~~~

List of default variables available in the inventory:

::

    ---
    
    # FQDN address of the Box Backup server to use
    # Set to False to disable boxbackup role
    boxbackup: False
    
    # Allow access to boxbackup server through firewall
    # Set to list of IP addresses / network ranges to allow access only from these
    # networks. Set to False to disable access
    boxbackup_allow: True
    
    # Directory where boxbackup-server is storing backups
    boxbackup_storage: '/srv/boxbackup'
    
    # boxbackup-server is listening on this IP address (all interfaces by default)
    boxbackup_listenAddresses: '0.0.0.0'
    
    # Enable/Disable verbose logging
    boxbackup_verbose: 'no'
    
    # 32-bit hexadecimal number representing the boxbackup-client account on the server
    # By default it is computed automatically as: 'ansible_fqdn | sha1sum | cut -c1-8'
    boxbackup_account: ""
    
    # Soft limit for storage space in megabytes, by default it's calculated as
    # total disk space of a given host. When used space is bigger than this,
    # boxbackup-server starts to remove old and deleted data
    boxbackup_softlimit:
    
    # Hard limit for storage space in megabytes. by default it's calculated as
    # soft limit * multiplier (see below). When used space reaches this limit,
    # server refuses to accept new data
    boxbackup_hardlimit:
    
    # Additional disk space added to soft limit, in megabytes. If this number is
    # negative, you will substract given amount of disk space from calculated soft
    # limit
    boxbackup_softlimit_padding: 1024
    
    # Hard limit multiplier will by default set hard limit to equal
    # soft limit + 50%. If you set this number lower than 1.0, you will have
    # smaller hard limit than soft limit, which is not a good idea
    boxbackup_hardlimit_multiplier: 1.5
    
    # Email address which will receive alerts from boxbackup. By default it's
    # <backup@localhost>, which is usually aliased to root account
    boxbackup_email: 'backup'
    
    # List of directories to back up; directory is a hash key, optional
    # exclude/include directives should be written as a text block. Examples can be
    # found in the /etc/boxbackup/bbackupd.conf config file
    boxbackup_locations:
      '/etc': |
        ExcludeFile = /etc/boxbackup/bbackupd/{{ boxbackup_account }}-FileEncKeys.raw
    
      '/home':
    
      '/opt':
    
      '/root':
    
      '/srv':
    
      '/usr/local':
    
      '/var': |
        ExcludeDir = /var/spool/postfix/dev
    
    # List of additional directories / mount points to back up, format is the same
    # as a list above
    boxbackup_locations_custom:

List of internal variables used by the role:

::

    boxbackup_account
    boxbackup_hardlimit
    boxbackup_softlimit


Authors and license
~~~~~~~~~~~~~~~~~~~

``boxbackup`` role was written by:

- Maciej Delmanowski | `e-mail <mailto:drybjed@gmail.com>`_ | `Twitter <https://twitter.com/drybjed>`_ | `GitHub <https://github.com/drybjed>`_

License: `GPLv3 <https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29>`_

****

This role is part of the `DebOps`_ project. README generated by `ansigenome`_.

.. _DebOps: http://debops.org/
.. _Ansigenome: https://github.com/nickjj/ansigenome/
