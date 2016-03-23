Getting started
===============

.. contents::
   :local:

Client configuration
--------------------

The ``debops.apt_cacher_ng`` role will use the ``debops.nginx`` role to
configure a proxied access to the cache over a custom subdomain, by default
``software-cache.{{ ansible_domain }}``. This subdomain should be configured in the
DNS and point to the server where the proxy is installed. You can open this
address in a web browser to access the web interface Apt-Cacher NG.

To use the Apt-Cacher NG proxy, the host can ether access the cache directly or
over the configured :program:`nginx` reverse proxy:

#. To configure direct cache connections include the following line in your inventory::

    apt__proxy_url: 'http://software-cache.<domain>:3142/'

#. To use the :program:`nginx` reverse proxy include the following line in your inventory::

    apt__proxy_url: 'http://software-cache.<domain>/'

The ``debops.apt`` role will ensure, that the host uses the given proxy server.

.. note:: Currently, for HTTPS repositories a direct connection to the destination domain
   will be used and the proxy server will not be used at all.
   This might be changed in the future. See
   `this GitHub issue <https://github.com/debops/ansible-apt_cacher_ng/issues/1>`_ for more
   information.

Example inventory
-----------------

To setup Apt-Cacher NG on host given in
``debops_service_apt_cacher_ng`` Ansible inventory group:

.. code:: ini

    [debops_service_apt_cacher_ng]
    hostname

Example playbook
----------------

Here's an example playbook that can be used to install and manage Apt-Cacher NG::

    ---

    - name: Install and manage the caching HTTP proxy Apt-Cacher NG.
      hosts: [ 'debops_service_apt_cacher_ng' ]
      become: True

      roles:

        - role: debops.etc_services
          tags: [ 'role::etc_services' ]
          etc_services__dependent_list:
            - '{{ apt_cacher_ng__etc_services__dependent_list }}'
            - '{{ nginx_apt_preferences_dependent_list }}'

        - role: debops.apt_preferences
          tags: [ 'role::apt_preferences' ]
          apt_preferences__dependent_list:
            - '{{ apt_cacher_ng__apt_preferences__dependent_list }}'

        - role: debops.ferm
          tags: [ 'role::ferm' ]
          ferm__dependent_rules:
            - '{{ apt_cacher_ng__ferm__dependent_rules }}'
            - '{{ nginx_ferm_dependent_rules }}'

        - role: debops.nginx
          tags: [ 'role::nginx' ]
          nginx_servers:
            - '{{ apt_cacher_ng__nginx__servers }}'
          nginx_upstreams:
            - '{{ apt_cacher_ng__nginx__upstream }}'

        # - role: debops.contrib-apparmor
        #   tags: [ 'role::apparmor' ]
        #   apparmor__local_dependent_config: '{{ apt_cacher_ng__apparmor__dependent_config }}'
        #   apparmor__tunables_dependent: '{{ apt_cacher_ng__apparmor__tunables_dependent }}'

        - role: debops.apt_cacher_ng
          tags: [ 'role::apt_cacher_ng' ]

