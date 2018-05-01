Introduction
============

The ``debops.elastic_co`` Ansible role can be used to configure APT
repositories maintained by the `Elastic <https://www.elastic.co/about>`_
company on Debian and Ubuntu hosts. The APT repositories are used to distribute
``elasticsearch``, ``logstash``, ``kibana``, ``filebeat``, ``metricbeat``,
``packetbeat`` and ``heartbeat`` APT packages. The role allows only for
installation of packages, additional configuration and management of the
installed software is performed by other Ansible roles.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.2.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.elastic_co

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
