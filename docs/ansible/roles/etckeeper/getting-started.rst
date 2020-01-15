Getting started
===============

.. contents::
   :local:

.. _etckeeper__ref_python3only:

etckeeper disabled in Python3-only environment
----------------------------------------------

At the moment, :command:`etckeeper` package in Debian `depends on Python 2.7`__
to work, due to the :command:`bzr` command `not yet ported to Python 3.x`__.
To avoid installation of Python 2.7 environment in Python 3.x-only
environments, the :command:`etckeeper` installation will be disabled by default
if the Python 2.7 environment is not already installed and detected by the
:ref:`debops.python` Ansible role.

.. __: https://bugs.debian.org/906000
.. __: https://bugs.debian.org/883146

You can override this behaviour by setting the :envvar:`etckeeper__enabled`
variable to ``True`` explicitly in the Ansible inventory. Alternatively, ensure
that the Python 2.7 environment is enabled by :ref:`debops.python` by setting
the :envvar:`python__v2` variable to ``True``.


Initial configuration
---------------------

By default :command:`git` is used as VCS. This can be changed via the
:envvar:`etckeeper__vcs` variable through Ansible inventory.

The role is designed with :command:`etckeeper` being already installed on
a host in mind. This can be done for example via Debian Preseeding or LXC
template installing and pre-configuring :command:`etckeeper`; the role will
keep the already existing configuration without any changes if the variables
are not overwritten through the Ansible inventory. Any changes in the
:file:`/etc/` directory will be automatically committed by Ansible local facts
before Ansible role execution.


Example inventory
-----------------

The ``debops.etckeeper`` role is part of the default DebOps playbook and run on
all hosts which are part of the ``[debops_all_hosts]`` group. To use this role
with DebOps it's therefore enough to add your host to the mentioned host group
(which most likely it is already):

.. code-block:: none

   [debops_all_hosts]
   hostname


Example playbook
----------------

Here's an example playbook that uses the ``debops.etckeeper`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/etckeeper.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::etckeeper``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
