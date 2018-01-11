Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

``debops.fcgiwrap`` role will by default disable the system-wide ``fcgiwrap``
instance. In its place you will be able to create per-user ``fcgiwrap``
instances, each with their own socket, running as an unprivileged user.

Each instance will make sure that specified user account and group exists, you
can specify additional configuration to create accounts with a specific shell or
home directory. By default system accounts (UID/GID < 1000) are used.

This role requires ``debops.core`` role to configure local fact which provides
the name of the init system used by the host (it does not need to be included
in the role dependencies, it's enough that it is run once at the beginning of
the playbook).

Example inventory
-----------------

To enable ``fcgiwrap`` on a host by hand, you need to add that host to
``[debops_service_fcgiwrap]`` host group in Ansible inventory. You will also
need to specify an instance to create. Example inventory::

    # inventory/hosts
    [debops_service_fcgiwrap]
    hostname

    # inventory/host_vars/hostname/fcgiwrap.yml
    fcgiwrap__instances:
      - name: 'webapp'
        user: 'webapp'
        group: 'webapp'
        home: '/srv/www/webapp'
        shell: '/bin/false'

This configuration will ensure that specified user account exists and will
start ``fcgiwrap`` on that account using system service script. The socket used
by this instance will be created as ``/run/fcgiwrap-webapp.socket``.

Example playbook
----------------

``debops.fcgiwrap`` is designed to be used from a playbook or a role as role
dependency. Here's an example configuration::

    ---
    - name: Set up web application
      hosts: [ 'debops_service_fcgiwrap' ]
      become: True

      roles:

        - role: debops.fcgiwrap
          tags: [ 'role::fcgiwrap' ]
          fcgiwrap__instances:
            - name: 'webapp'
              user: 'webapp'
              group: 'webapp'

