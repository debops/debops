.. Copyright (C) 2021 <imre@imrejonk.nl>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variables: configuration
================================

Some of the ``debops.pdns`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. _pdns__ref_configuration:

pdns__*_configuration
---------------------

The ``pdns__configuration``, ``pdns__group_configuration`` and
``pdns__host_configuration`` variables allow you to override
``/etc/powerdns/pdns.conf`` settings on a global, group or host basis. The
variables are lists of dicts that get merged using the principles of
:ref:`Universal Configuration <universal_configuration>`.

``name``
  Required. Name of the setting you want to change.

``comment``
  Optional. Comment added in the configuration file.

``value``
  Required. The value to configure as a string or YAML text block.

``state``
  Optional. The state of the setting in ``/etc/powerdns/pdns.conf``, either
  "present" or "absent". Defaults to "present".


Example::

  pdns__configuration:

    - name: 'also-notify'
      comment: |-
        Our secondary DNS provider uses unicast hosts to collect zone transfer
        data, and then distributes it internally to all their anycast servers.
      value: '2001:db8:a::1, 2001:db8:b::1, 2001:db8:c::1'
      state: '{{ "present"
                 if ansible_local.machine.deployment
                    |d("production") == "production"
                 else "absent" }}'
