.. _debops.rsyslog:

debops.rsyslog
==============

The `rsyslog <http://rsyslog.com/>`_ package is used to read, process, store
and forward system logs in different ways, on local or remote systems. The
``debops.rsyslog`` role can be used to easily configure log forwarding to
a central log server, as well as store logs on the filesystem or other storage
backends.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   unprivileged-tls

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/rsyslog/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
