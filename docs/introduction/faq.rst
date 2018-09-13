.. _faq:

Frequently Asked Questions
==========================

Here you can find answers to commonly asked questions about DebOps.

Can I use DebOps roles as standalone?
-------------------------------------

Yes! All [#f1]_ of the Ansible roles included in DebOps are designed to be
self-contained - each role usually manages a specific service or functionality,
and doesn't touch anything that it is not supposed to directly. Configuration
dependent on other roles (for example, firewall configuration for a network
service) is passed along to relevant roles using role dependent variables, on
the Ansible playbook level.

If you want, you can use DebOps roles in your own playbooks with completely
different dependent roles (for example replacing the :ref:`debops.ferm` role
with another firewall management Ansible role).

Some dependent roles like :ref:`debops.secret` and
:ref:`debops.ansible_plugins` are "hard dependencies" and without them roles
will not work as expected - check the example playbooks provided in the
documentation to see how the roles are used.


Why DebOps doesn't use :command:`ansible-vault` to store passwords?
-------------------------------------------------------------------

DebOps roles automatically generate randomized passwords for different accounts
and services, using the `password lookup plugin`__. To ensure idempotency,
plaintext passwords are stored on the Ansible Controller host in the
:file:`secret/` directory alongside the Ansible inventory.

.. __: https://docs.ansible.com/ansible/devel/plugins/lookup/password.html

The :command:`ansible-vault` command does not support automatic generation of
random passwords - you would need to `create each one by hand`__, which gets
tedious after the third host you manage. You can still do this if you want,
passwords used by DebOps roles are stored in variables which can be redefined
in the Ansible inventory.

.. __: https://docs.ansible.com/ansible/devel/vault.html

The :file:`secret/` directory is used for much more - Certificate Authority
management via :ref:`debops.pki`, passing secure data between hosts, for
example by :ref:`debops.tinc`, among other things. You can read more about it
in the :ref:`debops.secret` role documentation.


Ansible complains about ``"lookup plugin (*_src) not found"``.
--------------------------------------------------------------

DebOps playbooks and roles are supposed to be "read-only" to ensure that future
updates can be easily installed. To allow for more extensive modifications
(custom files, templates and tasks), a set of Ansible lookup plugins was
developed which allows to "inject" custom changes in the roles without
modifying the main files. These custom lookup plugins are not part of the
official Ansible distribution, and are `provided with the DebOps playbooks`__.

.. __: https://github.com/debops/debops/tree/master/ansible/playbooks/lookup_plugins

The error about lookup plugins not being present might show up if you use
DebOps roles separately from the main playbook, for example downloaded through
Ansible Galaxy. In this case the easiest solution is to download the custom
lookup plugins and provide them alongside your playbook, in
:file:`lookup_plugins/` directory; this should allow Ansible to find them and
use them.

The long term plan is to remove the need for the custom lookup plugins - the
roles that use them should be updated so that any changes that require custom
templates or files can be done through normal Ansible functionality.


Roles fail when running ``debops`` with the ``--skip-tags`` flag.
-----------------------------------------------------------------

This is due to the way tags are structured. As a general rule, if you use
``--skip-tags``, you should use tags in the form ``skip::<role_name>`` as
opposed to ``role::<role_name>``.

If the role you want to skip does not have a matching ``skip::<role_name>``
tag, please open an issue or, even better, create a pull request!

See `Issue #444`__ for more information and an example of such a pull
request.

.. __: https://github.com/debops/debops/issues/444


.. rubric:: Footnotes

.. [#f1] Well, almost all; some of the old roles might still mess with stuff
         outside of their scope, but we are working on fixing that. Stay tuned.
