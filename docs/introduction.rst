Introduction
============

The ``debops.redis`` role allows you to easily setup infrastructure capable of
running and managing 1 or more Redis servers. It is completely self healing
with Redis Sentinel and supports replication seamlessly.

Few features available in this role:

- seamless master/slave replication;
- throw together a master + n slaves + n sentinel setup in about 10 lines of YAML
  (most of those lines would be adding your hosts to the inventory);
- your configs are idempotent, even when redis rewrites them;
- pretty much every redis config value is tweakable;
- you can easily use this role as a dependency in your other roles;


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.redis

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
