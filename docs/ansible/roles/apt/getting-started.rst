Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

Role tries to detect the original APT repositories configured on the system and
use them in the generated :file:`/etc/apt/sources.list` configuration file. They
will be placed before the default repositories, with assumption that the
original repositories pointed to the closest mirror. The original APT
repositories can be completely disabled by setting ``apt__original_sources: []``
in your inventory.

The ``non-free`` repositories will be enabled automatically on hardware-based
hosts in case any non-free firmware is required. Otherwise, only the ``main``
and ``universe`` (on Ubuntu) repositories are enabled; you can control this
using the ``apt__nonfree`` variable.


Example inventory
-----------------

``debops.apt`` is included by default in the :file:`common.yml` DebOps playbook;
you don't need to do anything to have it executed.

If you don’t want to let ``debops.apt`` manage APT, you can do this with the
following setting in your inventory:

.. code-block:: yaml

   apt__enabled: False


If you have a local APT mirror that you want a group of hosts to use
exclusively, you could compose your inventory like this:

.. code-block:: yaml

   # Don't use the default mirrors
   apt__default_sources_state: 'absent'
   
   # Don't use the default security mirrors
   apt__security_sources_state: 'absent'
   
   # Replace the original APT mirror
   apt__original_sources: []
   
   # Define local APT mirror
   apt__group_sources:
     - uri:          'http://mirrors.domain.fqdn/debian'
       comment:      '{{ "Local " + apt__distribution + " repositories" }}'
       distribution: 'Debian'

   # Define local APT security mirrors
   apt__group_security_sources:
     - uri:          'http://mirrors.domain.fqdn/debian-security'
       comment:      '{{ "Local " + apt__distribution + " Security repository" }}'
       suite:        '{{ apt__distribution_release + "/updates" }}'
       distribution: 'Debian'


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apt`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/apt.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::apt``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
