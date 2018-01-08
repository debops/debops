Getting started
===============

Example inventory
-----------------

The ``debops.resources`` role is included by default in the :file:`common.yml`
DebOps playbook, you don't need to add hosts to any groups to enable it.

Role provides a special variable, :envvar:`resources__src` which points to
:file:`ansible/resources/` directory located in the DebOps project directory,
relative to the currently used Ansible inventory. This variable can be used in
the ``item.src`` keys of the file/archive lists to use the files from a central
location relative to the current DebOps project directory.

The :file:`ansible/resources/` directory is not created automatically, and role
does not check the existence of the specified files before using them.

An example usage:

.. code-block:: yaml

   resources__host_paths:
     - '/tmp/example-dir'

   resources__host_files:
     - src: '{{ resources__src + "file.txt" }}'
       dest: '/tmp/example-dir/file.txt'


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.resources`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/resources.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::resources``
  Main role tag, should be used in the playbook to execute all tasks.

``role::resources:paths``
  Manage paths on the remote hosts.

``role::resources:urls``
  Manage online resources on the remote hosts.

``role::resources:archives``
  Unpack archives on the remote hosts.

``role::resources:files``
  Manage file contents on the remote hosts.

``role::resources:delayed_paths``
  Manage delayed paths on the remote hosts.

