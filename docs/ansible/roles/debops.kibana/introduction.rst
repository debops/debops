Introduction
============

`Kibana <https://en.wikipedia.org/wiki/Kibana>`_ is a web interface which
can be used to display and analyze data stored in an Elasticsearch cluster. It
is a part of the Elastic Stack. The software is
developed by `Elastic <https://www.elastic.co/>`_.

The ``debops.kibana`` Ansible role can be used to deploy Kibana behind an
``nginx`` reverse proxy which connects to a local or remote Elasticsearch
cluster. The role can be used as a dependency by other Ansible roles to allow
control over their configuration options in the Kibana configuration file.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.kibana

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
