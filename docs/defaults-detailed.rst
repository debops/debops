Default variable details
========================

.. include:: includes/all.rst


Some of ``debops-contrib.dropbear_initramfs`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.


.. _dropbear_initramfs__ref_interfaces:

dropbear_initramfs__interfaces
------------------------------

The :envvar:`dropbear_initramfs__interfaces` and similar dictionaries behave
similar to the ``ifupdown__*_interfaces`` dictionaries of the debops.ifupdown_
role. Refer to the documentation of debops.ifupdown_ for details.

Compared to the debops.ifupdown_, only a limited subset of parameters is
currently supported:

``type``
  Optional. Anything other than ``ether`` will be ignored.

``inet``
  Optional. IPv4 configuration method used by a given interface.
  If you set this parameter to ``False``, no IPv4 configuration will be
  applied.
  Currently only ``static`` (default) and ``False`` is supported.

``inet6``
  Optional. IPv6 configuration method used by a given interface.
  If you set this parameter to ``False``, no IPv6 configuration will be
  applied.
  Currently only ``static`` (default) and ``False`` is supported.

``address`` or ``addresses``
  Optional. A string or a list of IPv4 and/or IPv6 addresses to set on
  a given network interface, in the form of ``ipaddress/prefix`` or CIDR.
  Remember that you need to specify the host IP address and not the network;
  the ``192.0.2.1/24`` is the correct notation, and ``192.0.2.0/24`` is
  incorrect.

``gateway`` or ``gateways``
  Optional. Specify the IPv4 or IPv6 address of the network gateway to which outgoing
  packets will be directed. If it's a list of addresses, first valid address
  for a network type will be used as the gateway.

Examples
~~~~~~~~

Configure ``eth0`` with a global IPv6 address.

.. literalinclude:: examples/dropbear_initramfs__interfaces.yml
   :language: yaml


.. _dropbear_initramfs__ref_authorized_keys:

dropbear_initramfs__authorized_keys
----------------------------------------

The :envvar:`dropbear_initramfs__authorized_keys` and similar variables are
used to define what SSH keys should be allowed for remote initramfs login.
Each list item is a dictionary with the following supported options:

``sshkeys``
  Required. String containing either a SSH public key, or an URL to a resource
  which returns a file with SSH public keys (only one URL is allowed at the
  moment), or a list of SSH public keys.

``options``
  Optional. String or list of SSH options which should be set for each key
  specified on the ``item.sshkeys`` list.
  Refer to :manpage:`dropbear(8)` for details.

  If this parameter is not specified, SSH public keys will use options set in
  the :envvar:`dropbear_initramfs__authorized_keys_options` variable. To
  override this variable for a particular entry, set the ``item.options``
  parameter as empty string or list.

  The specified SSH key options are applied to all keys specified in the
  ``item.sshkeys`` parameter in this specific entry. To use different key
  options for different SSH keys, specify them in separate entries on the list.

``key_options``
  Optional. Additional set of options to add to the SSH public keys. This can
  be used with ``item.options`` parameter to easily combine a list of options
  from another variable with a custom additional options.

``exclusive``
  Optional, boolean. If defined and ``True``, the role will remove all other
  SSH public keys and set only the SSH public keys defined by ``item.sshkeys``.

``state``
  Optional. If undefined or ``present``, the SSH public keys specified in the
  ``item.sshkeys`` parameter will be added. If ``absent``, the specified SSH
  public keys will be removed.

Examples
~~~~~~~~

Set SSH keys from a file on the Ansible Controller as the only allowed keys for
remote initramfs login:

.. literalinclude:: examples/dropbear_initramfs__authorized_keys.yml
   :language: yaml

Ensure that given SSH public keys are allowed for remote initramfs login:

.. literalinclude:: examples/dropbear_initramfs__group_authorized_keys.yml
   :language: yaml
