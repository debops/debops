Introduction
============

The `Postscreen <http://www.postfix.org/POSTSCREEN_README.html>`_ Postfix
service can be enabled to filter out undesired SMTP clients on initial
connection to the mail server. Postscreen uses certain criteria (static
white/blacklist, DNS Block List queries, communication analysis) to allow or
deny connections for a given SMTP client.

This role can be used to enable and configure Postscreen in a Postfix
installation managed by the :ref:`debops.postfix` Ansible role. It does not configure
Postfix directly on its own.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.postscreen

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
