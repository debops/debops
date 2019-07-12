.. _debops.phpipam:

debops.phpipam
==============

`phpIPAM`_  is an open-source web IP address management application (IPAM).
Its goal is to provide light, modern and useful IP address management.
It is php-based application with MySQL database backend, using jQuery
libraries, ajax and HTML5/CSS3 features.


The ``debops.phpipam`` role installs this ipam on a specified host with
nginx as a webserver (using :ref:`debops.nginx`).

.. _phpIPAM: https://phpipam.net/

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.phpipam/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
