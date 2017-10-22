Introduction
============

.. include:: includes/all.rst

The ``debops-contrib.volkszaehler`` role allows to setup your own volkszaehler.org_ instance.
volkszaehler.org is a free smart meter implementation with focus on data privacy.

A volkszaehler instance consists of a middleware written in PHP which is backed by a SQL database.
The middleware provides an API for frontends to query data and for controllers to insert data.

This role installs the default middleware together with the
default/bundled HTML/JavaScript frontend.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.5``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops-contrib.volkszaehler

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
