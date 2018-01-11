Default variable details
========================

Some of ``debops.persistent_paths`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _persistent_paths__ref_paths:

persistent_paths__paths
-----------------------

:envvar:`persistent_paths__paths` and similar dictionary variables
can be used to manage the persistence of paths.

The dictionary key should be used to bundle different paths together which are needed to achieve one goal.
This allows to mask/overwrite them later in the hierarchy as defined by :envvar:`persistent_paths__combined_paths`.
For use as dependency role, the key should be ``{{ weight }}_{{ role_owner }}_{{ role_name }}{{ optional_tags }}``
where ``weight`` should be a two-digit number. For DebOps roles, the weight ``50`` should be used.
For direct use, the key could be ``70_local_mlocate`` for example.

Each dictionary value is a dictionary by itself with the following supported options:

``paths``
  Required, list of strings. Paths to make persistent.
  The same path can be required to be persistent by multiple parties.

``state``
  Optional, string. Defaults to ``present``.
  Options:

  ``present``
    The paths should be persistent.

  ``absent``
    The paths are not required to be persistent. A possibly existing persistent
    state is not removed by this. Note that other parties might still require
    paths to be persistent which is not effected by setting one entry to ``absent``.

``by_role``
  Optional, string. Name of the Ansible role in the format
  ``{{ role_owner }}.{{ role_name }}`` which is responsable for the entry.
  This option probably only makes sense in the use as dependency role.

Examples
~~~~~~~~

.. literalinclude:: examples/persistent_paths.yml
   :language: yaml
