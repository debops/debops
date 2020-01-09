Default variable details
========================

Some of ``debops.debops_legacy`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _debops_legacy__ref_remove_diversions:

debops_legacy__remove_diversions
--------------------------------

The ``debops_legacy__remove_*_diversions`` variables define the
:command:`dpkg-divert` diversions that will be removed by the role. The
existing files will be deleted and the original files diverted by DebOps will
be moved back into place.

The variables are list with YAML dictionaries, each dictionary defines one file
with specific parameters:

``name``
  Required. Absolute path of the file that will be reverted. This parameter is
  used as a key for merging different configuration entries together.

``diversion``
  Optional. Absolute path of the diverted file to revert into its original
  place. If not specified, the filename is defined as:

  .. code-block:: none

     {{ item.name }}.dpkg-divert

``state``
  Optional. If not specified or ``present``, the existing diversion will be
  kept in place. If ``absent``, the diversion will be removed.

  If ``ignore``, a given configuration entry will not be evaluated by the role
  during execution, allowing conditional activation of the tasks.

Examples
~~~~~~~~

Remove existing diversion of a configuration file:

.. code-block:: yaml

   debops_legacy__remove_diversions:

     - name: '/etc/default/application'
       state: 'absent'


.. _debops_legacy__ref_remove_packages:

debops_legacy__remove_packages
------------------------------

The ``debops_legacy__remove_*_packages`` variables define the
APT packages which should be removed by the role. The variables are list of
YAML entries, each entry defines one APT package to remove using specific
parameters:

``name``
  Required. Name of the APT package to remove.

``state``
  Optional. If not specified or ``present``, the existing APT package will be
  kept in place, or installed if it's not present. If ``absent``, existing APT
  package will be removed.

  If ``ignore``, a given configuration entry will not be evaluated by the role
  during execution, allowing conditional activation of the task.

Examples
~~~~~~~~

Remove existing package conditionally, else leave the existing state
(installed/uninstalled) as is:

.. code-block:: yaml

   debops_legacy__remove_packages:

     - name: 'application'
       state: '{{ "absent"
                  if (ansible_hostname == "example")
                  else "ignore" }}'


.. _debops_legacy__ref_remove_files:

debops_legacy__remove_files
---------------------------

The ``debops_legacy__remove_*_files`` variables define the files or directories
which should be removed by the role. The variables are list of YAML entries,
each entry defines one file or directory to remove using specific parameters:

``name``
  Required. Absolute path of the file or directory to remove.

``state``
  Optional. If not specified or ``present``, the existing file will be left in
  place. Non-existent files or directories will result in an error. If
  ``absent``, existing file or directory will be removed.

  If ``ignore``, a given configuration entry will not be evaluated by the role
  during execution, allowing conditional activation of the task.

Examples
~~~~~~~~

Remove existing file conditionally based on Ansible facts:

.. code-block:: yaml

   debops_legacy__remove_files:

     - name: '/etc/default/application'
       state: '{{ "absent"
                  if (ansible_hostname == "example")
                  else "ignore" }}'
