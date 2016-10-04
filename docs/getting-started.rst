Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

Role tries to detect the original APT repositories configured on the system and
use them in the generated :file:`/etc/apt/sources.list` configuration file. They
will be placed before the default repositories, with assumption that the
original repositories pointed to the closest mirror.

The ``non-free`` repositories will be enabled automatically on hardware-based
hosts in case any non-free firmware is required. Otherwise, only the ``main``
and ``universe`` (on Ubuntu) repositories are enabled; you can control this
using the :envvar:`apt__nonfree` variable.


Example inventory
-----------------

``debops.apt`` is included by default in the :file:`common.yml` DebOps playbook;
you don't need to do anything to have it executed.

If you don’t want to let ``debops.apt`` manage APT, you can do this with the
following setting in your inventory:

.. code-block:: yaml

   apt__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apt`` role:

.. literalinclude:: playbooks/apt.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::apt``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
