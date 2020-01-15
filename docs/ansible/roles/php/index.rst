.. _debops.php:

debops.php
==========

The ``debops.php`` role can be used to manage PHP Hypertext Preprocessor
environment on a Debian/Ubuntu host. The role supports different PHP versions
available in OS distributions (PHP5, PHP7) with PHP-FPM service and multiple
PHP-FPM pools. Other Ansible roles can use it as a role dependency to offload
PHP management for their own use.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   upgrade

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/php/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
