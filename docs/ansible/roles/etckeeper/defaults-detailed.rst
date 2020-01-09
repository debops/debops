.. _etckeeper__ref_defaults_detailed:

Default variable details
========================

Some of ``debops.etckeeper`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _etckeeper__ref_gitignore:

etckeeper__gitignore
--------------------

The ``etckeeper__*_gitignore`` variables configure the contents of a section in
the :file:`/etc/.gitignore` file managed by the ``debops.etckeeper`` role. This
file specifies which paths (directories, files) should be ignored by
:program:`etckeeper` and :program:`git`. You can check the :man:`gitignore(5)`
manual page for the allowed syntax.

Each entry in the list defined in the variables is a YAML dictionary with
specific parameters:

``name``
  Required. Name of a given entry. If the ``ignore`` parameter is not
  specified, the ``name`` parameter is used as-is, otherwise it's not included
  in the file.

``comment``
  Optional. A string or YAML text block with a comment that describes a given
  entry.

``ignore``
  Optional. String or YAML text block that contains the paths which should be
  present in the :file:`/etc/.gitignore` file, it will be added in the file
  as-is.

``state``
  Optional. If not specified or ``present``, a given entry will be included in
  the generated section. If ``absent``, and entry will be removed from the
  generated section.

Examples
~~~~~~~~

Don't include :file:`/etc/shadow` and :file:`/etc/shadow-` files in
:program:`etckeeper` repository:

.. code-block:: yaml

   etckeeper__gitignore:

     - name: 'ignore-shadow'
       ignore: |
         shadow
         shadow-
       comment: "Don't track shadow database"
