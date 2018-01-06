Introduction
============

`fail2ban`_ is a service which parses specified log files and can perform
configured actions when a given regexp_ is found. It's usually used to ban
offending IP addresses using ``iptables`` rules (only IPv4 connections are
supported at the moment).

.. _fail2ban: http://www.fail2ban.org/
.. _regexp: https://en.wikipedia.org/wiki/Regular_expression

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
