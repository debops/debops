.. _debops.kibana:

debops.kibana
=============

`Kibana <https://en.wikipedia.org/wiki/Kibana>`_ is a web interface which
can be used to display and analyze data stored in an Elasticsearch cluster. It
is a part of the Elastic Stack. The software is
developed by `Elastic <https://www.elastic.co/>`_.

The ``debops.kibana`` Ansible role can be used to deploy Kibana behind an
``nginx`` reverse proxy which connects to a local or remote Elasticsearch
cluster. The role can be used as a dependency by other Ansible roles to allow
control over their configuration options in the Kibana configuration file.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed
   dependency

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/kibana/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
