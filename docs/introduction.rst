Introduction
============

The ``at`` and ``batch`` commands can be used to compliment ``cron`` and run
one-off tasks either at a specified time, or when the host CPU utilization is on
a low enough level.

The ``debops.atd`` role can be used to configure ``atd`` service, including
randomized load average threshold and randomized time between batch job
execution, as well as access control to the ``at`` and ``batch`` commands by
the users.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.9.0``. To install it, run::

    ansible-galaxy install debops.atd

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
