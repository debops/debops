Introduction
============

.. include:: includes/all.rst

The ``debops-contrib.foodsoft`` role allows to setup your own Foodsoft_ instance.
Foodsoft is a web-based software to manage a non-profit food coop (product catalog,
ordering, accounting, job scheduling).

The role is based on the following documentation:

* `Deployment (Debian) <https://github.com/foodcoop-adam/foodsoft/wiki/Deployment-%28Debian%29>`__
* `SETUP_DEVELOPMENT.md <https://github.com/foodcoops/foodsoft/blob/master/doc/SETUP_DEVELOPMENT.md#manual-configuration>`__
* `Dockerfile <https://github.com/foodcoops/foodsoft/blob/master/Dockerfile>`__

Note that the author of this role currently does not have an production
deployment using this role but he will try to maintain this role as good as
possible.
He just wrote this role just for fun to try out Foodsoft.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.5``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops-contrib.foodsoft

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
