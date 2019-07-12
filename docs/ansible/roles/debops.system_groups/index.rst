.. _debops.system_groups:

debops.system_groups
====================

The UNIX system groups are used on Linux hosts for low level access control
mechanism for different system services. Debian by default creates a
`a set of UNIX system groups`__ which control access to various parts of the
system.

The ``debops.system_groups`` Ansible role is used to configure additional UNIX
system groups that are used on hosts managed by DebOps. It can also be used to
define :command:`sudo` and :command:`systemd-tmpfiles` configuration for these
UNIX groups.

Additionally, a simple Access Control List managed by the role in the Ansible
local facts can be used by other Ansible roles to configure access for selected
UNIX groups to the services managed by these roles.

.. __: https://wiki.debian.org/SystemGroups


.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.system_groups/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
