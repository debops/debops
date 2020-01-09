Default variable details
========================

Some of the ``debops.sysnews`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _sysnews__ref_entries:

sysnews__entries
----------------

The ``sysnews__*_entries`` lists can be used to add or manage permanent
System News entries in the :file:`/var/lib/sysnews/` directory. The variables
are combined in the order specified by the :envvar:`sysnews__combined_entries`
variable, entries with the same name are combined together; the entries later
in the list override parameters from previous entry with the same name.

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. Name of the text file located in the :file:`/var/lib/sysnews/`
  directory (spaces if the filename are permitted).

``src``
  Optional, conflicts with ``content``. Path to a text file located on the
  Ansible Controller, which should be put in the :file:`/var/lib/sysnews/`
  directory with a given name. By default the path is relative to the
  :file:`files/` directory of the ``debops.sysnews`` Ansible role.

``content``
  Optional, conflicts with ``src``. YAML text block which contains a text to
  put in a file in the :file:`/var/lib/sysnews/` directory with a given name.
  The text can contain Jinja templating which will be evaluated at Ansible
  execution time.

``state``
  Optional. Define the state of a particular news file. If multiple list
  entries define a file state, the last one wins. Recognized states:

  - not specified or ``present``: the file will be put in the
    :file:`/var/lib/sysnews/` directory.

  - ``absent``: the specified file will be removed.

  - ``ignore``: the given configuration entry will be ignored by the role. This
    can be used to conditionally activate or skip entries.


Examples
~~~~~~~~

Add a new, permanent System News entry:

.. code-block:: yaml

   sysnews__entries:

     - name: 'News about an application'
       content: |
         A new application has been installed and is ready to be used.

         Have a nice day.
       state: 'present'
