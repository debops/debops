Introduction
============

An NTP daemon is used for time synchronization, either on a local system as
a client, or on remote systems as a server.

The ``debops.ntp`` Ansible role supports multiple NTP servers, and is
container-aware so that an NTP server won't be installed inside containers.

The role is also used to configure the system timezone using the ``tzdata``
package.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.ntp

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
