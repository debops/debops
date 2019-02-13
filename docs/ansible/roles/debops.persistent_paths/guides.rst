.. _persistent_paths__ref_guides:

Usage guides
============

.. include:: ../../../includes/global.rst

Role authors who want to support platforms like `Qubes OS`_ and other
environments where persistence is not the default can do so by using this role
as a dependency role, either has hard or soft dependency (DebOps default).

The general mode of operation looks like this:

#. Your service role is run as usual writing to non-persistent paths.

#. ``debops.persistent_paths`` is run to ensure that paths specified by the
   service role are persistent.


To make this happen, you would typically include a default variable like
``role_name__persistent_paths__dependent_paths`` in your service role like this
one:

.. code-block:: yaml

   # .. envvar:: role_name__persistent_paths__dependent_paths [[[
   #
   # Configuration for the debops.persistent_paths_ Ansible role.
   role_name__persistent_paths__dependent_paths:

     '50_role_owner_role_name':
       by_role: 'role_owner.role_name'
       paths:
         - '/etc/example1'
         - '/etc/example2'
                                                                      # ]]]

And then pass this to ``debops.persistent_paths`` when calling the role:

.. code-block:: yaml

   - role: role_owner.role_name
     tags: [ 'role::role_name' ]

   - role: debops.persistent_paths
     tags: [ 'role::persistent_paths' ]
     persistent_paths__dependent_paths: '{{ role_name__persistent_paths__dependent_paths }}'

Note that as `Qubes OS`_ and similar platforms are not the main target
platforms of DebOps, an additional playbook which features
``debops.persistent_paths`` support should be included in roles instead of extending the default role playbook.
User can then select the role playbook they want to run using Ansible groups as needed.

Examples of roles which use/support ``debops.persistent_paths``:

* ``debops.cryptsetup``
* ``debops.dnsmasq``
* ``debops.tinc``


.. _persistent_paths__ref_guide_updating_persistent_files:

Templating or updating persistent files
---------------------------------------

Qubes OS supports persistent files or directories in TemplateBasedVM using bind
mounts. The files and directories marked for persistent storage are copied to
a separate directory and mounted over the original files.

Note that bind mounted files (and directories) don’t allow `rename` nor
`unlinkat` sys calls. This means that once a file has been made persistent by
bind mounting it, updates to the file needs to be done using the
``unsafe_writes`` parameter which many file related Ansible modules support.

Refer to the `debops.core usage guide <https://docs.debops.org/en/latest/ansible/roles/debops.core/guides.html#global-unsafe-writes>`_
for details.
