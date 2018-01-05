.. _apt_cacher_ng__ref_getting_started:

Getting started
===============

.. include:: ../../../includes/global.rst

.. contents::
   :local:

Client configuration
--------------------

The ``debops.apt_cacher_ng`` role will use the :ref:`debops.nginx` role to
configure a proxied access to the cache over a custom subdomain, by default
``software-cache.{{ ansible_domain }}``. This subdomain should be configured in the
DNS and point to the server where the proxy is installed. You can open this
address in a web browser to access the web interface of Apt-Cacher NG.

To use the Apt-Cacher NG proxy, hosts can either access Apt-Cacher NG
directly or via the configured :program:`nginx` reverse proxy:

#. To point hosts directly to the Apt-Cacher NG proxy server, include the
   following line in your inventory::

    apt_proxy__http_url: 'http://software-cache.<domain>:3142/'

#. To point hosts to the :program:`nginx` reverse proxy include the following
   line in your inventory::

    apt_proxy__http_url: 'http://software-cache.<domain>/'

The debops.apt_proxy_ role will ensure that the hosts use the given proxy server.

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

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apt_cacher_ng`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/apt_cacher_ng.yml
   :language: yaml

If you make extensive use of the flexibility of this role and are using
AppArmor you might need to use the following playbook instead:

.. literalinclude:: examples/apt_cacher_ng-apparmor.yml
   :language: yaml

The playbook is shipped with this role under
:file:`./docs/playbooks/apt_cacher_ng-apparmor.yml` from which you can symlink it to your
playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider
using the `DebOps Contrib playbooks`_.
