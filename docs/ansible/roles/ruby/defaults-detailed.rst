Default variable details
========================

Some of ``debops.ruby`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _ruby__ref_gems:

ruby__gems
----------

These lists can be used to install system-wide Ruby gems. Each element of
a list is either a name of a Ruby gem, or an YAML dictionary with parameters
for the ``gem`` Ansible module. See that module documentation for specific
parameter syntax. Some more important parameters are:

``name``
  Name of the Ruby gem which should be installed. If not specified, entire
  entry will be treated as a Ruby gem name.

``state``
  Optional. If not specified or ``present``, the gem will be installed
  system-wide. If specified and ``absent``, gem will be removed.

Examples
~~~~~~~~

Install custom Ruby gems on all hosts in the inventory:

.. code-block:: yaml

   ruby__gems:

     - 'mako'

     - name: 'nokogiri'
       state: 'present'

.. _ruby__ref_user_gems:

ruby__user_gems
---------------

These lists can be used to install Ruby gems on an user account. Unlike the
system-wide gems, you cannot specify simple gem names as list entries, only
YAML dictionaries are allowed. Each entry uses parameters supported by ``gem``
Ansible module, as well as some additional parameters:

``name``
  Required. Specify the name of a Ruby gem to install.

``owner``
  Required. Specify name of the user account on which the Ruby gem will be
  installed. If it does not exist, the user account will be automatically
  created as a system account, with its own primary group named after the
  account.

``user``
  Required if ``owner`` is not set. Specify the user account on which a given
  Ruby gem should be installed. The account needs to exist. To automatically
  create the account if needed, use the ``owner`` parameter.

``group``
  Optional. Specify the primary group of the user account which will be created
  by the role if it doesn't exist.

``home``
  Optional. Specify the path to the home directory of the newly-created user
  account. If not specified, the home directory path will be created
  automatically, based on the ``owner`` parameter.

``system``
  Optional, boolean. If not specified or ``True``, the new user account will be
  a "system" account, with UID and GID <1000. If specified and ``False``, the
  user account will be a normal user account.

``state``
  Optional. If not specified or ``present``, the gem will be installed
  on the user account. If specified and ``absent``, gem will be removed.

Examples
~~~~~~~~

Install Ruby gems on a specific user account, on all hosts. The user account
will be created if it doesn't exist:

.. code-block:: yaml

   ruby__user_gems:
     - name: 'mako'
       owner: 'application'

