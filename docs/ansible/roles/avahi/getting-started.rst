Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

By default the ``debops.avahi`` role publishes records for the SSH and SFTP
services, as well as a special ``device-info`` record which marks the server as
a "file server" on supported platforms. The ``workstation`` and ``hinfo``
records are not published to indicate that this host is a server and not
a client machine.


.. _avahi__ref_alias_support:

Avahi CNAME (alias) support
---------------------------

Avahi by default does not support ``CNAME`` records, i.e. alternative
subdomains that point to a given host. To support these records,
``debops.avahi`` can install and configure a custom third party script,
`avahi-alias <https://github.com/george-hawkins/avahi-aliases-notes>`_
maintained by `George Hawkins <https://github.com/george-hawkins>`_.

The script will be installed by default if the Python 2.7 support is enabled on
the host. At present (2019), Debian does not include the ``python3-avahi``
package, therefore Python 2.7 is required for this functionality to work.

The role will install the script in the :file:`/usr/local/sbin/` directory and
prepare a :command:`systemd` service (SysVinit is not supported at this time).
The script needs to be restarted to register any changed CNAME records and this
is not automatic unlike Avahi daemon itself (role restarts the service on any
changes).

The list of CNAME records is stored in the :file:`/etc/avahi/aliases` file and
can be modified by other roles or manually. The file should contain only CNAME
FQDN records, each in one line; comments are not supported.


Avahi services in other Ansible roles
-------------------------------------

The ``debops.avahi`` Ansible role is designed to be used as a role dependency
of another Ansible role. By specifying the service configuration using the
:envvar:`avahi__dependent_services` variable (preferably as a YAML list) you
can configure Avahi services as well as CNAME aliases if necessary.
See :ref:`avahi__ref_services` for more details about supported parameters.

If advanced control over CNAME aliases published by Avahi is not needed, you
can make the process simpler by including the tasks that configure an Avahi
service directly in your own role, for example:

.. literalinclude:: examples/avahi-tasks.yml
   :language: yaml

Avahi daemon automatically detects changes in the :file:`/etc/avahi/services/`
directory and reloads all files, therefore service restart is not necessary.
The format of the XML service file can be found in the
:man:`avahi.service(5)` manual page.


Example inventory
-----------------

The ``debops.avahi`` role needs to be enabled to be used in the DebOps
playbook. To do that, add the hosts that you want to configure Avahi on to the
``[debops_service_avahi]`` Ansible inventory group:

.. code-block:: none

   [debops_service_avahi]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.avahi`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/avahi.yml
   :language: yaml
