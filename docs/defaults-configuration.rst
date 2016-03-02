Default variables: configuration
================================

Some of ``debops.unattended_upgrades`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _unattended_upgrades__blacklist:

unattended_upgrades__blacklist
------------------------------

The ``unattended_upgrades__blacklist`` and similar lists allow you to specify
packages which shouldn't be upgraded automatically. You can specify them
as simple package names or dictionaries with specific keys:

``name``
  Required, string or list specifying a package name to include in the
  blacklist.

``when``
  Required. A conditional variable which should be evaluated to a boolean which
  will be tested by the ``debops.unattended_upgrades`` role. If the result is
  ``True``, the specified package(s) will be included in the blacklist.

Examples
~~~~~~~~

Include specified packages in the upgrade blacklist on all hosts:

.. code-block:: yaml

   unattended_upgrades__blacklist:

     - 'zsh'

     - name: 'postgresql'
       when: '{{ ansible_hostname in [ "database", "db" ] }}'

     - name: [ '^linux-*', 'vim' ]
       when: '{{ (ansible_local|d() and ansible_local.tags|d() and
                  "production" in ansible_local.tags) }}'

