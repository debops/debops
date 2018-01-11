Default variable details
========================

some of ``debops.tcpwrappers`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _tcpwrappers__allow:

tcpwrappers__allow
------------------

This is a list of ``/etc/hosts.allow`` entries defined as YAML dictionaries.
Each entry will be stored in ``/etc/hosts.allow.d/`` directory in a separate
file. The configuration roughly follows the conventions described in the
``hosts_access(5)`` and ``hosts_options(5)`` man pages. The list of known
parameters:

``daemon``
  Required. Name or list of names of the daemons which should be configured,
  the first entry will be used in th filename if a custom one is not specified.

``client``
  Optional. String or list of IP addresses, CIDR subnets, domain names and
  other "clients" that should be allowed (by default) to connect to a given
  service. If not specified, the access will be granted for all hosts, unless
  it's disabled by ``item.accept_any`` parameter.

  IPv6 addresses should be specified "as is", they will be automatically
  converted to square bracket notation.

``option``
  Optional. String or list of additional options for a particular entry. This
  will be added after list of clients. The colons (``:``) inside the options
  are automatically escaped by a backslash. See ``hosts_options(5)`` man page
  for possible values.

``custom``
  Optional. A YAML text block with raw configuration in ``/etc/hosts.allow``
  format.

``weight``
  Optional. Two-digit number prefix added to the entry filename, to allow
  easier sorting of files in ``/etc/hosts.allow.d/`` directory.

``filename``
  Optional. Custom name of the file stored in ``/etc/hosts.allow.d/``. If not
  specified, a name will be generated based on the value of ``item.daemon`` or
  ``item.daemons`` parameter.

``comment``
  Optional. A comment added to the given entry to explain its purpose.

``accept_any``
  Optional, boolean. If not specified or ``True``, without a specific client
  list the service that is being configured will acceppt connections from all
  hosts (``ALL``). If specified and ``False``, connections won't be allowed
  unless a list of clients is specified and not empty.

``state``
  Optional. Either ``present`` or ``absent``. If specified and ``absent``, the
  configuration file will be removed from ``/etc/hosts.allow.d/`` directory,
  otherwise it will be created.

Examples
~~~~~~~~

Allow connection from anywhere to ``sshd``:

.. code-block:: yaml

   tcpwrappers__allow:
     - daemon: 'sshd'

Restrict access to ``vsftpd`` daemon to a set of particular subnets (IPv6
addresses are wrapped in square brackets automatically):

.. code-block:: yaml

   tcpwrappers__allow:
     - daemon: [ 'vsftpd' ]
       client: [ '192.0.2.0/24', '2001:db8::/32' ]
       accept_any: False
