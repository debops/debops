Introduction
============

The :command:`apt-listchanges` package is used to notify system administrator about
package changes from Changelog and NEWS files. The role will configure this
script to send that information via email messages to specified addresses.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.apt_listchanges

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
