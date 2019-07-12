.. _debops.sysnews:

debops.sysnews
==============

This role can be used to manage "System News" bulletin displayed after users
log in to a particular host using local system console or SSH. System News can
be used to notify users about important changes on the host; this is especially
useful in multi-user environments or on bastion hosts.

The System News can be read by executing the :command:`news` command in the
shell. You can read all of the news entries by executing the :command:`news -a`
command.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.sysnews/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
