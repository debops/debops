Introduction
============

`Etherpad <https://en.wikipedia.org/wiki/Etherpad>`_ is a collaborative text
editor usable through a web browser. Documents can be edited by multiple people
in real time, shared and exported in different formats.

This role can be used to deploy and configure `Etherpad Lite <https://github.com/ether/etherpad-lite>`_,
a NodeJS version of Etherpad, on a Debian/Ubuntu host. The application can use
a MariaDB or SQLite database as a storage backend, and will be configured
behind a Nginx proxy as a frontend.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.etherpad

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
