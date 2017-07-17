.. _postfix__ref_defaults_detailed:

Default variable details
========================

.. include:: includes/all.rst

some of ``debops.postfix`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


postfix__maincf
---------------

Configuration of the ``postfix__*_maincf`` variables is described in a separate
document, :ref:`postfix__ref_maincf`.


postfix__mastercf
-----------------

Configuration of the ``postfix__*_mastercf`` variables is described in
a separate document, :ref:`postfix__ref_mastercf`.


.. _postfix__ref_maincf_sections:

postfix__maincf_sections
------------------------

The :file:`/etc/postfix/main.cf` configuration file is managed using informal
"sections", each section groups the common Postfix options.

The :envvar:`postfix__maincf_sections` variable contains a list of sections defined
by YAML dictionaries with specific parameters:

``name``
  Required. Short name of the section, used in the configuration
  parameters to put a given option in a particular section.

``title``
  Optional. A short description of the section included as its header.

``state``
  Optional. If not specified or ``present``, the section will be added in the
  configuration file. If ``absent``, the section will not be included in the
  file.

Examples
~~~~~~~~

Define a set of configuration sections:

.. code-block:: yaml

   postfix__maincf_sections:

     - name: 'base'

     - name: 'admin'
       title: 'Administrator options'

     - name: 'unknown'
       title: 'Other options'
