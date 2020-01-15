.. _debops.fcgiwrap:

debops.fcgiwrap
===============

`fcgiwrap`_ is a lightweight FastCGI server which can be set up behind
``nginx`` server to run CGI applications. This role allows you to setup
separate instances of ``fcgiwrap`` on different user accounts, each one
accessible through its own UNIX socket.

.. _fcgiwrap: https://github.com/gnosek/fcgiwrap

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/fcgiwrap/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
