Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

The role forwards the ``root`` mail to a set of e-mail administrator accounts
defined by the :ref:`debops.core` Ansible role (see that role's documentation for
more details). If they are not defined, the mail will be forwarded to
``root@<domain>`` for convenience.

The role creates the ``staff`` mail alias which by default is forwarded to
``root``. If you have separate team for IT Operations and Helpdesk, you might
want to consider changing this, or some other aliases to forward mail
elsewhere. To do that, you can define in the inventory:

.. code-block:: yaml

   etc_aliases__recipients:

     # Forward staff mail to specific users
     - staff: [ 'example1', 'example2' ]

     - example1: 'user1@example.com'

     - example2: 'user2@example.com'

See the :ref:`etc_aliases__ref_recipients` for more details about
the configuration format.


Support for the RFC 2142
------------------------

The :rfc:`2142`: Mailbox Names For Common Services and Functions
defines a set of mailboxes (or aliases) that are recommended to exist on any
DNS domain to allow easy communication between organizations. This role defines
these recommended mail aliases by default for convenience. You can disable this
by setting the variable:

.. code-block:: yaml

   etc_aliases__rfc2142_compliant: False

Alternatively, you can change the default mail recipients for the created
aliases using the normal configuration mechanism described above.


Example inventory
-----------------

To configure ``debops.etc_aliases`` on a given remote host, it needs to be added to
``[debops_service_etc_aliases]`` Ansible inventory group:

.. code-block:: none

    [debops_service_etc_aliases]
    hostname


Example playbook
----------------

Here's a minimal example playbook that can be used to manage the
:file:`/etc/aliases` file:

.. literalinclude:: ../../../../ansible/playbooks/service/etc_aliases.yml
   :language: yaml

The playbook is shipped with this role under
:file:`docs/playbooks/etc_aliases.yml` from which you can symlink it to your
playbook directory.
