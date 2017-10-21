Default variable details
========================

Some of the ``debops.etc_aliases`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _etc_aliases__ref_recipients:

etc_aliases__recipients
-----------------------

The ``etc_aliases__*_recipients`` variables define mail aliases and their
recipients which should be present in the :file:`/etc/aliases` file. Each
variable is a YAML list with dictionaries as the entries. Multiple entries that
define the same mail alias are combined together in order of appearance.

Each entry can be a YAML dictionary with a dictionary key being the alias to
define, and dictionary value being a string with one recipient, or a YAML list
of recipients to set for a given alias:

.. code-block:: yaml

   etc_aliases__recipients:

     - root: 'admin'

     - admin: [ 'user1', 'user2' ]

The more complex version uses a set of parameters that allow greater control
over a particular alias:

``name``, ``alias``
  The mail alias to configure.

``dest``, ``to``
  Required. The string or an YAML list of recipients for a given mail alias.

``add_dest``, ``add_to``, ``cc``, ``bcc``
  Optional. A string or an YAML list of recipients to add to existing list of
  recipients. This is useful in subsequent entries to modify the list of
  recipients if necessary.

``del_dest``, ``del_to``
  Optional. A string or an YAML list of recipients to remove from the existing
  list of recipients. This is useful in subsequent entries to modify the list
  of recipients if necessary.

``comment``
  Optional. A string or YAML text block with a comment added to a particular
  alias.

``state``
  Optional. If not specified or ``present``, a given alias entry will be
  defined in the database file.

  If ``absent``, the alias will not be included in the database file.

  If ``hidden``, the entry itself won't be included, but the optional comment
  will be in the file.

  If ``comment``, the entry will be present in the database file, but commented
  out.

``section``
  Optional. Name of the section in the database file in which a given alias
  should be included. If not specified, the ``unknown`` section is used
  automatically.

``weight``
  Optional. A numeric value which is used to sort the entries in the final
  database file. The entries with higher numbers have bigger "weight" and will
  be put lower in the file. Negative numbers can be used to put the entries
  higher than normal. If not specified, a default ``0`` will be set.

Examples
~~~~~~~~

Create a set of aliases:

.. code-block:: yaml

   etc_aliases__recipients:

     - name: 'root'
       dest: 'admin'

     - alias: 'admin'
       to: [ 'user1', 'user2' ]

     - alias: 'admin'
       cc: 'user3'


.. _etc_aliases__ref_sections:

etc_aliases__sections
---------------------

The :file:`/etc/aliases` file is managed using informal "sections", each
section groups the common mail aliases. The :envvar:`etc_aliases__sections`
contains a list of sections defined by YAML dictionaries with specific
parameters:

``name``
  Required. Short name of the section, used in the alias configuration
  parameters to put the aliases in a particular section.

``title``
  Optional. A short description of the section included as its header.

``state``
  Optional. If not specified or ``present``, the section will be added in the
  database file. If ``absent``, the section will not be included in the file.

Examples
~~~~~~~~

Define a set of alias sections:

.. code-block:: yaml

   etc_aliases__sections:

     - name: 'general'
       title: 'General-purpose mail aliases'

     - name: 'admin'
       title: 'Administrator mail aliases'

     - name: 'unknown'
       title: 'Other mail aliases'
