Introduction
============

`phpIPAM`_  is an open-source web IP address management application (IPAM).
Its goal is to provide light, modern and useful IP address management.
It is php-based application with MySQL database backend, using jQuery
libraries, ajax and HTML5/CSS3 features.


The ``debops.phpipam`` role installs this ipam on a specified host with
nginx as a webserver (using :ref:`debops.nginx`).

.. _phpIPAM: https://phpipam.net/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.4``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.phpipam

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
