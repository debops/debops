.. Copyright (C) 2020      Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later


.. _universal_configuration:

Universal Configuration
=======================

An important pillar of the DebOps workflow is the idea that roles and playbooks
should not be modified directly, but are expected to be fully configurable
purely through inventory variables.

In order to tackle this challenge, DebOps uses a set of jinja2 filters to
implement an idiomatic variable syntax called **Universal Configuration**.

The syntax allows *lists of uniquely named items* to be built up from multiple
sources, with later occurrences of items with the same name modifying earlier
ones.

Apart from simple aggregation, Universal Configuration provides ways to:

- Attach *comments* to specific list items
- Manipulate the *state* of list items
- Manipulate the order of the resulting lists via a *weight* mechanism
- Express values in a shorthand way when advanced functionality isn't required

Overall, this approach allows roles to focus on the specifics of the
applications they are intended to manage while presenting a clean, flexible
and consistent interface to configure them with pin-point accuracy.

So, without further ado, let's get down to brass tacks.


.. _universal_configuration_input:

Input styles
------------

Universal Configuration list items always end up as *mappings* in role tasks
and templates. Apart from their intended values, these mappings include a
number of reserved terms that roles implement to provide the functionality
mentioned above.


.. _universal_configuration_input_kv:

Key-Value pairs
~~~~~~~~~~~~~~~

In their simplest form, list items are mappings containing ``name`` and
``value`` keys.

.. code-block:: yaml

   - name: 'foo'
     value: 'bar'

   - name: 'fizz'
     value: 'buzz'


.. _universal_configuration_input_short:

Shorthand items
~~~~~~~~~~~~~~~

Depending on what the list is used for, the ``value`` field may be redundant.
In such cases, the short-form syntax allows providing ``name`` as a string.

.. code-block:: yaml

   - 'foo'
   - 'bar'

   # Long-form may be mixed with short-form when required.
   - name: 'fizz'
     comment: 'buzz'


.. _universal_configuration_input_mappings:

Arbitrary mappings
~~~~~~~~~~~~~~~~~~

Universal Configuration items are not limited to strings or key-value pairs,
but may be arbitrary mappings.

.. code-block:: yaml

   - name: foo

     # Filter control keys
     comment: 'bar'
     weight: 9001

     # Role-specific keys
     file: '/etc/fizzbuzz'
     widget_length: 42


The constraints of valid usage will, of course, depend on what you are
configuring. Apart from the reserved terms that affect Universal Configuration
behavior, all other keys in the mapping get passed to the implementing role.


.. _universal_configuration_tutorial:

Simple usage tutorial
---------------------

As previously mentioned, Universal Configuration's main utility has to do with
aggregating lists of items from multiple sources.

Before we get to examining some of the more advanced capabilities the syntax
affords us when dealing with lists, let's go over some of the more ubiquitous
usage patterns that you're sure to encounter while working with DebOps.

Let's imagine a ``paperclip_maximizer`` role, that defines the following
default variables:

.. code-block:: yaml

   paperclip_maximizer__default_products:

     - name: 'paperclip'
       material: 'scrap metal'

       # Sane default to avert world-ending scenario!
       value: 8999

     - name: 'production capacity'
       material: 'ethically sourced lithium'
       value: 42

   paperclip_maximizer__products: []

   paperclip_maximizer__combined_products: '{{
       paperclip_maximizer__default_products
       + paperclip_maximizer__products
   }}'

In this configuration pattern:

- Our own variables are meant to live in ``paperclip_maximizer__products``
- The role's entry point is ``paperclip_maximizer__combined_products``

As the comment in the role's defaults makes clear, under no circumstances are
we to mess with the ``value`` field. But what are we to do?
Replicating the ``value`` in our own configuration exposes us to the equally
horrifying scenario of violating the **DRY** principle!


.. _universal_configuration_merging:

Modifying defaults
~~~~~~~~~~~~~~~~~~

List items with the same name get merged with each other, the ones that appear
later overriding earlier ones.

.. code-block:: yaml

   paperclip_maximizer__products:

     - name: 'paperclip'
       material: 'carbon fiber'
       comment: 'Our paperclips only use space-age materials!'

In this example, our inventory will modify only the key we care about, and add
a comment in the resulting configuration.

This way we avoid hardcoding a value we don't care about and allow future
updates to propagate through our configuration, in case best practices change.


.. _universal_configuration_state:

Removing items
~~~~~~~~~~~~~~

As often encountered in other Ansible features, Universal Configuration items
implement a ``state`` functionality.

Roles may implement more states as needed, but you can expect ``present`` and
``absent`` to always work.

.. code-block:: yaml

   paperclip_maximizer__products:

     - name: 'paperclip'
       state: 'absent'

     - name: 'flowerpot'
       material: 'clay'
       value: 64

This example removes the default ``paperclip`` product and repurposes the role
to create flowerpots instead.


.. _universal_configuration_weight:

Reordering items
~~~~~~~~~~~~~~~~

Our flowerpot maximizer is almost ready!
However, due to made up role constraints, list item order is important.

Fortunately, Universal Configuration items implement a ``weight`` mechanic:

- Items with a negative weight float upwards
- Items with a positive weight sink downwards

.. code-block:: yaml

   paperclip_maximizer__products:

     - name: 'paperclip'
       state: 'absent'

     - name: 'flowerpot'
       material: 'clay'
       value: 64
       weight: -50


And here we go. Now the role knows to prioritize ``flowerpot`` production,
without ``production capacity`` hogging all the clay!


.. _universal_configuration_patterns:

More configuration patterns
---------------------------

Apart from the *default* pattern, where ``role__default_list`` variables are
merged with a list containing user configuration, a couple more distinct
patterns can be commonly encountered throughout the DebOps codebase.

In all cases, the role entry point to those lists is a ``role__combined_list``
variable.


.. _universal_configuration_all_group_host:

The *all/group/host* pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This pattern allows each level of inventory variables to overload the previous
one. It is commonly used for role variables that are additive in nature.

.. code-block:: yaml

   role__combined_list: '{{
       role__default_list
       + role__list
       + role__group_list
       + role__host_list
   }}'


.. _universal_configuration_dependent:

The *dependent* pattern
~~~~~~~~~~~~~~~~~~~~~~~

*Dependent* configuration lists are used when roles are loaded as dependencies
of other roles. They look like ``role__dependent_list`` and are included
towards the end of ``role__combined_list`` variables.

.. code-block:: yaml

   role__combined_list: '{{
       role__default_list
       + role__list
       + role__dependent_list
   }}'

Dependent configurations are empty when the role runs on its own, and are
populated in playbooks from other roles' dependent variables.

In this next example, the ``nginx`` role populates the ``ferm`` role's
dependent variables in order to open the ``http`` and ``https`` ports:

.. code-block:: yaml

   - role: ferm
     tags: [ 'role::ferm', 'skip::ferm' ]
     ferm__dependent_rules:
       - '{{ nginx__ferm__dependent_rules }}'

Although this list also gets the Universal Configuration treatment, using it to
modify elements appearing in previous lists it will lead to idempotence issues
and is to be avoided.


.. _universal_configuration_advanced:

Advanced list behavior
----------------------

In this section, we will go over some of the more complex aspects of Universal
Configuration.

Most of these are not as universally required when using the majority of roles
and when they are the role documentation will give you fair warning.


.. _universal_configuration_option:

Controlled merging
~~~~~~~~~~~~~~~~~~

Items use ``name`` as a unique key. The underlying filter *does* allow a role
to change the name of the field used for this purpose, by providing a ``name``
argument,  but for consistency it is generally discouraged unless there's a
*really* compelling reason to do so.

This has the implication that configuration options which *may* appear multiple
times in valid configuration would override each other if naively implemented.

The ``option`` field exists for this purpose:

.. code-block:: yaml

   - name: 'timeout'
     value: 2 * 60 * 60

   - name: 'my first include'
     option: 'include'
     value: '/etc/fizz'

   - name: 'my other include'
     option: 'include'
     value: '/etc/buzz'

In this example, our two ``include`` statements can coexist and be modified
as expected by later items targeting their ``name`` field.

The role can then loop through the resulting list in its templates with a
single statement like the one below:

.. code-block:: jinja

  {{ '{} = {}'.format((item.option | d(item.name)), item.value) }}


.. _universal_configuration_advanced_weight:

Weighing and anchoring
~~~~~~~~~~~~~~~~~~~~~~

Under the hood, the configuration filters populate an ``id`` field for each
item in multiples of 10, starting from 0.

An item's ``weight`` is added to that ``id`` to come up with the final sorting
order, stored in a field called ``.real_weight``.

.. note::

   Take note that the initial order of the list items matters as much as
   the ``weight`` you provide.

   The specifics of the weight behavior can be counterintuitive and are
   currently under review. Don't build too intricate orderings that you
   cannot afford to rewrite, and watch this space!


In more complex scenarios, the ``copy_id_from`` key allows us to reference
another list item by ``name``. Its ``real_weight`` will then be calculated
based on that referenced item's ``id``.


.. _universal_configuration_recursion:

Recursion
~~~~~~~~~

If an item's ``value`` or the special ``options`` field contains a list,
the configuration filters will recurse into it, so any of the documented
configuration syntax can be used in it as well.

Values contained in those fields **will be merged** between items with the same
``name`` and passed through the filter, so you can expect them to behave
exactly as the top level merged lists.

Roles may enable recursive merging for other fields as well.
Those cases will be clearly stated in the implementing role's documentation.

Populating a ``value`` field that has already been initialized as a list with
a single value, such as a string, will override it and stop any subsequent
merging.

.. note::

   The behavior applies only to the first level of items passed through the
   list. Lists as values nested in item values will not be parsed.


.. note::

   When merging items with the same ``name`` whose ``value`` fields contain
   lists, the underlying ``parse_kv_items`` filter **will not merge** them,
   but override them instead. Only the last appearing ``value`` will be used.

   Those cases are clearly stated in the implementing role's documentation.


Further reading
---------------

You now know all there is to know to competently use even the most advanced
features of DebOps Universal Configuration.

If you want to read more about implementing the syntax in your roles,
check out the role development guide.

- :ref:`ansible_plugins_config_filters` documentation
- `YAML syntax`__ on the Ansible documentation
- `YAML Version 1.2`__ Specification

.. __: https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html
.. __: https://yaml.org/spec/1.2/spec.html

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
