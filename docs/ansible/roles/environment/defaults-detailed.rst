Default variable details
========================

Some of ``debops.environment`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _environment__ref_variables:

environment__variables
----------------------

The environment variable lists can use different formats of list entries.

Strings:

.. code-block:: yaml

   environment__variables:

     - 'variable1=value1'

     - 'variable2=value2'

     - 'variable3=value3'

YAML dictionaries of variables:

.. code-block:: yaml

   environment__variables:

     - variable1: 'value1'
       variable2: 'value2'
       variable3: 'value3'

YAML dictionaries of conditional variables - they are detected when ``name``
and ``value`` keys are used in the same YAML dictionary:

.. code-block:: yaml

   environment__variables:

     - name: 'variable1'
       value: 'value1'

     - name: 'variable2'
       value: 'value2'
       state: 'absent'

     - name: 'variable3'
       value: 'value3'
       upper: True

When the conditional variables are detected, you can specify these parameters:

``name``
  Required. Name of the environment variable.

``value``
  Required. Value of the environment variable.

``state``
  Optional. If not specified or ``present``, variable will be set in the
  ``/etc/environment`` file. If ``absent``, variable will not be included. The
  role does not remove already set variables in the ``/etc/environment`` file
  outside of the Ansible block.

``case``
  Optional. Change the case of the variable name, either ``upper`` or
  ``lower``. If not set, the current case will be preserved.

To set the ``name`` and ``value`` variables in the environment, you need to
specify them separately:

.. code-block:: yaml

   environment__variables:

     - name: 'value1'

     - value: 'value2'

