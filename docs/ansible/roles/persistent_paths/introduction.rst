Introduction
============

.. include:: ../../../includes/global.rst
.. include:: includes/role.rst

This role provides a generic mechanism to declare which files/directories
are required to be persistent. How this information is used can then be defined in
this role.

On `Qubes OS`_, all work gets done in AppVMs which are typically based on
TemplateVMs.  Only a few paths in such TemplateBasedVM will persist a reboot,
mainly :file:`/home` and :file:`/rw`. Package installation and the like is
supposed to happen in TemplateVMs only but configuration can happen in either
VM type as desired. If changes should be made in a TemplateBasedVM however it
needs to be made sure that they are persistent.

Since Qubes OS R3.2 the bind-dirs_ script and related configuration can be used
to easily make additional paths persistent by bind mounting them from
:file:`/rw/bind-dirs/` to the desired path.

``debops.persistent_paths`` allows other Ansible roles to interact with
bind-dirs_ by using this role as a dependency role.
An example which does this is ``debops.cryptsetup``.

The role can also be used by the system administrator to manage bind-dirs_
using the Ansible inventory.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.4``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.persistent_paths

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
