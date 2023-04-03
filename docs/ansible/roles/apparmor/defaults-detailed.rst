.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.apparmor`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _apparmor__ref_profiles:

apparmor__profiles
------------------

The ``apparmor__*_profiles`` variables define which profiles should be
enabled or disabled, following the principles of
:ref:`universal configuration <universal_configuration>`.

Examples
~~~~~~~~

Define the state of a couple of profiles:

.. code-block:: yaml

   apparmor__profiles:

     - name: 'usr.sbin.nmbd'
       state: 'complain'

     - name: 'usr.sbin.smbd'
       state: 'enforce'

     - name: 'usr.sbin.traceroute'
       state: 'disable'

     - name: 'usr.local.sbin.legacy'
       state: 'ignore'

Syntax
~~~~~~

The AppArmor profile configuration options uses YAML dictionaries with the
following parameters:

``name``
  Required. Name of the profile under the :file:`/etc/apparmor.d/` directory.
  Configuration entries with the same ``name`` parameter are merged in order of
  appearance; this can be used to change configuration options conditionally.

``state``
  Required. The desired state of the given profile. Valid states are:

  ``enforce``
    Results in the enforcement of the policy defined in the profile; policy
    violation attempts will be blocked and logged.

  ``complain``
    The policy will not be enforced (with some caveats, as noted in the
    :man:`aa-complain(8)` man page, `deny` rules are still enforced), but
    policy violations will be logged.

  ``disable``
    The policy will not be loaded; policy violations will be neither blocked
    nor logged.

  ``ignore``
    The state of the given policy will not be changed. This is useful to
    override more generic configuration.


.. _apparmor__ref_locals:

apparmor__locals
----------------

The ``apparmor__*_locals`` variables define modifications to system
profiles. The variables define file fragments which are placed under
:file:`/etc/apparmor.d/local/`, and can be used to fine-tune existing profiles
to meet site-specific requirements.

In order to determine the correct name for an override, have a look at the
profile which needs to be further customized:

.. code-block:: console

   # cat /etc/apparmor.d/usr.sbin.nscd
   ...
     # Site-specific additions and overrides. See local/README for details.
     #include <local/usr.sbin.nscd>
   }

Here, the relevant modification for :file:`/etc/apparmor.d/usr.sbin.nscd`
would be :file:`/etc/apparmor.d/local/usr.sbin.nscd`. The ``debops.apparmor``
role will automatically prepend the :file:`/etc/apparmor.d/local/` part, so
the modification should simply be named :file:`usr.sbin.nscd`.

This is the case for most profiles.

As noted in :file:`/etc/apparmor.d/local/README`:

.. note::
   Keep in mind that 'deny' rules are evaluated after allow rules, so you won't
   be able to allow access to files that are explicitly denied by the shipped
   profile using this mechanism.

Examples
~~~~~~~~

Define modifications for two profiles (showing three different possible
syntaxes for a given configuration option):

.. code-block:: yaml

   apparmor__locals:

     - name: 'usr.sbin.dnsmasq'
       options:

         - name: 'dnsmasq-allow-resolvconf'
           comment: 'Allow dnsmasq to read upstream DNS servers'
           option: '/etc/resolvconf/upstream.conf'
           value: 'r'

         - name: '/etc/hosts.dnsmasq'
           value: 'r'

     - name: 'usr.bin.pidgin'
       options:

         - name: 'pidgin-allow-home-plugins'
           comment: 'Allow per-user Pidgin plugins'
           raw: '@{HOME}/.purple/plugins/** rm,'

.. _apparmor__ref_locals_syntax:

Syntax
~~~~~~

The AppArmor profile modification options uses YAML dictionaries with the
following parameters:

``name``
  Required. Name of the local modification file under the
  :file:`/etc/apparmor.d/local/` directory. Note that subdirectories are also
  supported, so if ``name`` is set to :file:`foo/bar`, the result will be
  written to :file:`/etc/apparmor.d/local/foo/bar`.
  Configuration entries with the same ``name`` parameter are merged in order of
  appearance; this can be used to change configuration options conditionally.

``state``
  Optional. If not specified or ``present``, the configuration file will be
  created, or a given configuration option (see ``options`` below) will be
  present in the configuration file. If ``absent``, a given file/option will be
  removed. If ``init`` or ``ignore``, the configuration file/option won't be
  created/included - this can be used e.g. to prepare configuration that will
  be activated conditionally someplace else. If ``comment``, a given
  configuration option will be present, but commented out.

``options``
  Optional. A list of YAML dictionaries with options which should be written to
  the modification file, valid parameters include ``name`` and ``state``, as
  explained above, plus the following parameters:

  ``option``
    Optional. A string which, if defined, will be used instead of the ``name``
    parameter when generating the configuration file.

  ``value``
    Optional. A string which will be used together with ``name`` or ``option``
    to generate a line in the generated configuration file.

  ``operator``
    Optional. A string defining the operator used to combine the ``name`` or
    ``option`` and ``value`` in the generated configuration file. The default
    is a space (unless the template detects that a different operator should
    be used, based on the ``name`` or ``option``).

  ``suffix``
    Optional. A string which should be added at the end of the configuration
    option in the generated configuration file. The default is a comma.

  ``raw``
    Optional. String or YAML text block which will be included in the generated
    configuration file "as is". If the ``raw`` parameter is defined, it takes
    precedence over ``name``, ``option``, ``value``, ``operator`` and
    ``suffix``.

  ``comment``
    Optional. String or YAML text block with comments about a given
    configuration option.

  ``separator``
    Optional, boolean. If defined and ``True``, the role will add an empty line
    before a given configuration option, to allow for better readability.

  ``weight``
    Optional. Positive or negative number which defines the additional "weight"
    of an option. Smaller or negative weight will move the option higher in the
    configuration file, higher weight will move the configuration option lower
    in the configuration file.

  ``options``
    Optional. Same format as ``options`` above. An option which contains
    suboptions will be rendered as a configuration block with the ``option``
    or ``name`` value of the parent option as the name of the configuration
    block.

The TL;DR; version is that options will generally be rendered in the generated
configuration file as:

.. code-block:: none

   (option.option | option.name) + option.operator + option.value + option.suffix

So a configuration like this:

.. code-block:: yaml

   - name: 'usr.sbin.named'
     options:

       - name: '/etc/pki/**'
         operator: ' '
         value: 'r'
         suffix: ','

Is equivalent to a configuration like this:

.. code-block:: yaml

   - name: 'usr.sbin.named'
     options:

       - name: 'allow-pki-access'
         option: '/etc/pki/**'
         value: 'r'

And both will result in the following line being included in the generated
configuration file:

.. code-block:: none

   /etc/pki/** r,

.. _apparmor__ref_tunables:

apparmor__tunables
------------------

The ``apparmor__*_tunables`` variables are similar to the
:ref:`apparmor__ref_locals` variables, but instead define the content of
file fragments in the :file:`/etc/apparmor.d/tunables/` directory.

The tunables which are supported depends on the profiles which are already
installed, and covering them all is outside the scope of this documentation.

See the existing files under :file:`/etc/apparmor.d/tunables/` to get a
better feeling for what is possible and not. Also, see the `tunables`__ section
from the Ubuntu wiki for more details.

.. __: https://wiki.ubuntu.com/DebuggingApparmor#Adjusting_Tunables

Examples
~~~~~~~~

Define an additional path under which user home directories are stored:

.. code-block:: yaml

   apparmor__tunables:

     - name: 'home.d/site.local'
       options:

         - name: 'add-home-dirs'
           comment: 'Define additional home directory locations'
           option: '@{HOMEDIRS}'
           operator: '+='
           value: '/srv/nfs/home/ /mnt/home/'

Syntax
~~~~~~

The AppArmor tunables options use YAML dictionaries with the same syntax as
:ref:`apparmor__locals<apparmor__ref_locals_syntax>`.

The only difference is that the default value for ``operator`` is ``=`` and
the default value for ``suffix`` is no suffix.
