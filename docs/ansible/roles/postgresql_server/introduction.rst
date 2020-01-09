Introduction
============

.. include:: ../../../includes/global.rst

`PostgreSQL`_ is a popular relational open source database. This role can be
used to install and manage a set of PostgreSQL clusters on Debian-based
systems. You can use :ref:`debops.postgresql` role to configure roles and
databases on local or remote PostgreSQL servers.

.. _PostgreSQL: http://www.postgresql.org/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.9.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.postgresql_server

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
