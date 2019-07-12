.. _debops.machine:

debops.machine
==============

The ``debops.machine`` Ansible role [#f1]_ manages basic information about
a given host located in the :file:`/etc/machine-info` configuration file, as
well as static and dynamic Message Of The Day (MOTD) shown after login, and the
contents of the :file:`/etc/issue` file displayed on the `system console`__.

.. __: https://en.wikipedia.org/wiki/System_console

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.machine/COPYRIGHT

.. rubric:: Footnotes

.. [#f1] Name of this role was based on the :file:`/etc/machine-info`
         configuration file, and is loosely connected to the concept of the
         "Machine" defined in the `Site Reliability Engineering`__ book.

.. __: https://landing.google.com/sre/book/chapters/production-environment.html

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
