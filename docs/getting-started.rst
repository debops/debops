Getting started
===============

.. contents::
   :local:

Default setup
-------------

If you don't specify any configuration values, the role will setup a `nginx`_
HTTP server running a default installation of the latest Roundcube stable
release which is then accessible via ``https://roundcube.<your-domain>``.

.. _nginx: https://github.com/debops/ansible-nginx

Example inventory
-----------------

You can install Roundcube on a host by adding it to the
``[debops_service_roundcube]`` Ansible group in your Ansible inventory::

    [debops_service_roundcube]
    hostname

Example playbook
----------------

Here's an example playbook which uses the ``debops-contrib.roundcube`` role to install
Roundcube:

.. literalinclude:: playbooks/roundcube.yml
   :language: yaml
