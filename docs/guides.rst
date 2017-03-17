.. _persistent_paths__ref_guides:

Usage guides
============

.. include:: includes/all.rst

.. _persistent_paths__ref_guide_updating_persistent_files:

Templating or updating persistent files
---------------------------------------

Qubes OS supports persistent files or directories in TemplateVMs using bind
mounts. The files and directories marked for persistent storage are copied to
a separate directory and mounted over the original files.

Note that bind mounted files (and directories) don’t allow `rename` nor
`unlinkat` sys calls. This means that once a file has been made persistent by
bind mounting it, updates to the file should be redirected to the actual
location (called ``storage_path`` by this role).

This can be achieved by:

#. Running the service role the first time as usual writing to non-persistent paths.

#. Letting the service role create an Ansible local fact at the end of the role
   run. This fact, combined with the ``debops.persistent_paths`` facts will be
   used to determine when Ansible should be redirected.

#. Running the ``debops.persistent_paths`` role to copy the changes made to a
   persistent location and providing them at the non-persistent path.

#. If the service role is now run again, the problematic file operations need
   to be done against the ``storage_path``.

To do this, you can introduce a new default role variable like this one:

.. code-block:: yaml

   # .. envvar:: role_name__persistent_prefix_path [[[
   #
   # Directory path prefix which should be used for writing/updating of files made
   # persistent by :envvar:`role_name__persistent_paths__dependent_paths`.
   role_name__persistent_prefix_path: '{{ ansible_local.persistent_paths.storage_path|d("")
                                          if (ansible_local|d() and
                                              ansible_local.role_name|d() and
                                              ansible_local.role_name.enabled|d() | bool and
                                              ansible_local.persistent_paths|d() and
                                              ansible_local.persistent_paths.enabled|d() | bool and
                                              ansible_local.persistent_paths.write_to_storage_path|d() | bool)
                                          else "" }}'
                                                                      # ]]]

And use ``role_name__persistent_prefix_path`` as prefix in tasks:

.. code-block:: yaml

   - name: Template the configuration file
     template:
       src: 'etc/role_name/config.ini'
       dest: '{{ role_name__persistent_prefix_path }}/etc/role_name/config.ini'

This way, when Ansible detects that the role has been configured and persistent
paths are enabled, all involved tasks should be redirected to the correct
location automatically.

Refer to `Clarify some issues regarding bind-dirs <https://github.com/QubesOS/qubes-doc/pull/299#discussion_r106387538>`_ for more details.
