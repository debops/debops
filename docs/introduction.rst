Introduction
============

.. include:: includes/all.rst

The debops.mailman_ Ansible role can be used to create and manage mailing
lists using `GNU Mailman <http://list.org/>`_ package.

By default the role provides configuration for debops.postfix_ role to
configure the SMTP server integration, as well as debops.nginx_ role to
configure access to the web control panel.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run::

    ansible-galaxy install debops.mailman

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
