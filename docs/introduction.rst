Introduction
============

The ``debops.cron`` Ansible role can be used to manage :command:`cron` jobs
through Ansible inventory. You can define :command:`cron` jobs at different
levels of Ansible inventory (all hosts, a group of hosts, specific hosts) and
manage custom files or scripts required by the jobs.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.cron

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
