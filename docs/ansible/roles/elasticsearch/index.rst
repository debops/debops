.. _debops.elasticsearch:

debops.elasticsearch
====================

`Elasticsearch <https://en.wikipedia.org/wiki/Elasticsearch>`_ is a distributed
search engine and storage system, also a part of the Elastic Stack.
The software is developed by `Elastic <https://www.elastic.co/>`_.

The ``debops.elasticsearch`` Ansible role can be used to deploy and manage
Elasticsearch instances on one or more (3+) hosts. The role can be used as
a dependency by other Ansible roles to allow control over their configuration
options in the Elasticsearch configuration file.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed
   clustering
   dependency

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/elasticsearch/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
