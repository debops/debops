Introduction
============

`DokuWiki`_ is an easy to use, file-based wiki written in PHP5.
``debops.dokuwiki`` role installs this wiki on a specified host with nginx
as a webserver (using :ref:`debops.nginx`). You can optionally
configure multiple DokuWiki instances with shared base installation using
`DokuWiki vhost farm`_ mode.

.. _DokuWiki: https://www.dokuwiki.org/
.. _DokuWiki vhost farm: https://www.dokuwiki.org/farms

Installation
------------

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.dokuwiki

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
