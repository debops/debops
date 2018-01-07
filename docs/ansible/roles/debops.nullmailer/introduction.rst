Introduction
============

The `nullmailer <http://untroubled.org/nullmailer/>`_ package can be used to
setup a forwarding SMTP relay. It does not provide support for local mail, but
forwards all messages to one or more remote SMTP servers for processing.

The ``debops.nullmailer`` role installs and configures the ``nullmailer``
service, optionally with a network access from remote hosts on port 25.

The role can detect other Mail Transport Agents installed on the managed host,
and if an MTA from a configurable list is found, the role will automatically
disable itself to allow easy switch to different SMTP servers.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.nullmailer

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
