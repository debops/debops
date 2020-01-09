Introduction
============

`fcgiwrap`_ is a lightweight FastCGI server which can be set up behind
``nginx`` server to run CGI applications. This role allows you to setup
separate instances of ``fcgiwrap`` on different user accounts, each one
accessible through its own UNIX socket.

.. _fcgiwrap: https://github.com/gnosek/fcgiwrap

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.8.0``. To install it, run::

    ansible-galaxy install debops.fcgiwrap

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
