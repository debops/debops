Introduction
============

`OpenSSH`_ is a secure replacement for ``telnet`` and other remote control
programs. It allows you to connect to remote hosts over a encrypted communication
channel and to perform a variety of tasks. It's also the primary communication channel
used by Ansible.

.. _OpenSSH: http://www.openssh.com/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.sshd

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
