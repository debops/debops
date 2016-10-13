Introduction
============

.. include:: includes/all.rst

``debops.elasticsearch`` role allows you to easily setup infrastructure
capable of running Elasticsearch. Few features available in this role:

- seamless clustering
- easily pick node types through groups and also allow you to do it manually
- add/remove plugins and libs on demand, you can even set custom
  configuration to each plugin, check the defaults
- tweak pretty much everything that ES allows you to


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.elasticsearch

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
