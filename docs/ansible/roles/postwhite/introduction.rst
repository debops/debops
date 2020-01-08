Introduction
============

The `Postwhite <https://github.com/stevejenkins/postwhite>`_ script can be used
to generate whitelists and/or blacklists of IP addresses and CIDR subnets based
on the SPF records of selected domains. These whitelists/blacklists can then be
used by the `Postscreen <http://www.postfix.org/POSTSCREEN_README.html>`_
Postfix service to automatically allow or deny connections to specific SMTP
clients. This is useful for accepting messages from big mail providers like
Google and Outlook which may resend mail messages from different IP addresses,
which in turn interferes with Postscreen SMTP client greylisting.

The ``debops.postwhite`` Ansible role will install Postwhite script and
configure Postfix automatically using the :ref:`debops.postfix` Ansible role, as long
as the Postscreen configuration is enabled by the :ref:`debops.postscreen` role.
See the documentation of the mentioned roles for more details.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.postwhite

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
