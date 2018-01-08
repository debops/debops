Introduction
============

This `Ansible`_ role allows you to manage a backup host which will use
`rsnapshot`_ to create remote backups of other hosts. You can let Ansible
configure both the central backup "clients", which run :program:`rsnapshot` and store
backups, as well as the "servers" which the clients connect to, which run
:command:`rsync`` in read-only mode on ``root`` accounts.

You can also configure :program:`rsnapshot` clients to backup external hosts which are
not managed by Ansible, but you will need to set up the connection (SSH access,
:command:`rrsync` script) yourself on the server side.

.. _Ansible: http://ansible.com/
.. _rsnapshot: http://www.rsnapshot.org/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
