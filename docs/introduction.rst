Introduction
============

``debops.postfix`` is an `Ansible`_ role which installs and manages `Postfix`_,
an SMTP server. It is designed to manage Postfix on different hosts in
a cluster, with different "capabilities".

Features
--------

At the moment role can configure Postfix to act as:

- a null client: Postfix sends all mail to another system specified
  either via DNS MX records or an Ansible variable, no local mail is enabled
  (this is the default configuration);

- a local SMTP server: local mail is delivered to local user accounts;

- a network SMTP server: network access is enabled separately from other
  capabilities, to avoid exposing misconfigured SMTP server by mistake and
  becoming an open relay;

- an incoming MX gateway: Postfix will listen on the port 25 (default SMTP
  port) and process connections using ``postscreen`` daemon with automatic
  greylisting and optional RBL checking;

- an outgoing SMTP client: Postfix will relay outgoing mail messages to
  specified remote MX hosts, you can optionally enable SMTP client
  authentication, passwords will be stored separate from the inventory in
  ``secret/`` directory (see ``debops.secret`` role). Sender dependent
  authentication is also available.

More "capabilities" like user authentication, support for virtual mail,
spam/virus filtering and others will be implemented in the future.

This role can also be used as a dependency of other roles which then can
enable more features of the Postfix SMTP server for their own use. For
example, ``debops.mailman`` role enables mail forwarding to the configured
mailing lists, and ``debops.smstools`` role uses Postfix as mail-SMS gateway.

.. _Ansible: http://ansible.com/
.. _Postfix: http://postfix.org/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
