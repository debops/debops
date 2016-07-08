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
address in a web browser to access the web interface of Apt-Cacher NG.

To use the Apt-Cacher NG proxy, the host can either access the Apt-Cacher NG
directly or via the configured :program:`nginx` reverse proxy:

#. To point hosts directly to the Apt-Cacher NG proxy server, include the
   following line in your inventory::

    apt__proxy_url: 'http://software-cache.<domain>:3142/'

#. To point hosts to the :program:`nginx` reverse proxy include the following
   line in your inventory::

    apt__proxy_url: 'http://software-cache.<domain>/'

The ``debops.apt`` role will ensure that the hosts use the given proxy server.

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

Here's an example playbook that can be used to install and manage Apt-Cacher NG:

.. literalinclude:: playbooks/apt_cacher_ng.yml
   :language: yaml
