Default variable details
========================

Some of ``debops.mosquitto`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _mosquitto__ref_options:

mosquitto__options
------------------

The :envvar:`mosquitto__default_options` and :envvar:`mosquitto__options`
variables are YAML dictionaries which contain global Mosquitto configuration
stored in the :file:`/etc/mosquitto/conf.d/00_default.conf` configuration file.
They are combined together, therefore it is possible to override the default
options using the Ansible inventory. The Mosquitto configuration reference can
be found in the :man:`mosquitto.conf(5)` manual page.

Each key of the YAML dictionary is a Mosquitto option name. Dictionary keys
cannot be specified by variable substitution. If the value is a string, it is
set as-is for a given option. If the string value is empty (''), the option
will be removed from the configuration file.

If the value is a YAML list, each list element will be present in its own line
with the option name prepended to it.

Boolean values are not processed by the template, you should use the string
representation accepted by Mosquitto (``'true'``, ``'false``) in the variable,
or use an ``if/else`` condition that interprets boolean values and passes
correct strings as needed.

Examples
~~~~~~~~

Set a few custom options for Mosquitto:

.. code-block:: yaml

   # A few variables set in the Ansible inventory as an example
   mqtt_connection_messages: False
   mqtt_log_dest: 'syslog'
   mqtt_log_type: [ 'all', 'debug', 'warning', 'notice' ]
   mqtt_log_timestamp: 'true'

   mosquitto__options:
     connection_messages: '{{ "true" if mqtt_connection_messages|bool else "false" }}'
     log_dest:            '{{ mqtt_log_dest }}'
     log_type:            '{{ mqtt_log_type if mqtt_log_dest == "syslog" else "" }}'
     log_timestamp:       '{{ mqtt_log_timestamp }}'

The above configuration should result in:

.. code-block:: none

   log_timestamp true
   connection_messages false
   log_dest syslog
   log_type all
   log_type debug
   log_type warning
   log_type notice


.. _mosquitto__ref_listeners:

mosquitto__listeners
--------------------

The :envvar:`mosquitto__default_listeners` and :envvar:`mosquitto__listeners`
variables can be used to configure how Mosquitto listens for connections. The
variables are YAML dictionaries, which are combined together, therefore the
default configuration can be easily changed through Ansible inventory if
needed. There's no custom merging, if you want to modify a specific listener,
you need to include all of its options.

Each entry in the YAML dictionary is a listener configuration. The dictionary
key can be anything, but it's best to specify the TCP port the listener will be
configured on, for consistency. The value of the dictionary is another YAML
dictionary, with keys being the :command:`mosquitto` configuration options, and
values being the option values; the format is similar to the one used in the
:ref:`mosquitto__ref_options` configuration. You can find the possible
configuration options and their meaning in the ``LISTENERS`` section of the
:man:`mosquitto.conf(5)` manual page.

The role knows about additional listener parameters, which are used to manage
the configuration:

``comment``
  Optional. A custom comment added to the listener, either a string or a YAML
  text block.

``state``
  Optional. If not specified or ``present``, the listener configuration will be
  generated on the host. If ``absent``, the listener configuration will be
  removed.

The listener configuration can contain additional parameters that are not used
by Mosquitto, but are used to configure Avahi services (see
:ref:`mosquitto__ref_avahi_support` for more details):

``avahi_type``
  Required for Avahi support. The string that specifies the service type, for
  example ``_mqtt._tcp``.

``avahi_port``
  Required for Avahi support. The port number the service is listening for
  connections, which will be advertised by Avahi.

``avahi_state``
  Optional. If not specified or ``present``, the Avahi configuration for
  a given listener will be generated. If ``absent``, the Avahi configuration
  for a given listener will be removed.

You can check the :envvar:`mosquitto__default_listeners` variable in the
:file:`defaults/main.yml` file for examples of the Mosquitto listener
configuration.


.. _mosquitto__ref_bridges:

mosquitto__bridges
------------------

The :envvar:`mosquitto__bridges`, :envvar:`mosquitto__group_bridges` and
:envvar:`mosquitto__host_bridges` variables can be used to configure bridge
connections between MQTT brokers (Mosquitto or other brokers). The variables
are YAML dictionaries, which are combined together, therefore the default
configuration can be easily changed through Ansible inventory if needed.
There's no custom merging, if you want to modify a specific bridge, you need to
include all of its options.

Each entry in the YAML dictionary is a bridge configuration. The dictionary key
should be a short name of the bridge; it can also be specified as the
``connection`` parameter. The value of the dictionary is another YAML
dictionary, with keys being the :command:`mosquitto` configuration options, and
values being the option values; the format is similar to the one used in the
:ref:`mosquitto__ref_options` configuration. You can find the possible
configuration options and their meaning in the ``CONFIGURING BRIDGES`` section
of the :man:`mosquitto.conf(5)` manual page.

The role knows about additional bridge parameters, which are used to manage
the configuration:

``comment``
  Optional. A custom comment added to the bridge, either a string or a YAML
  text block.

``state``
  Optional. If not specified or ``present``, the bridge configuration will be
  generated on the host. If ``absent``, the bridge configuration will be
  removed.

Examples
~~~~~~~~

The example bridge connection to the `test Mosquitto broker <http://test.mosquitto.org>`_
from the manual page:

.. code-block:: yaml

   mosquitto__bridges:
     'test-mosquitto-org':
       address: 'test.mosquitto.org'
       cleansession: 'true'
       topic: 'clients/total in 0 test/mosquitto/org/ $SYS/broker/'

An example two-directional bridge connection to central Mosquitto broker on
local domain over TLS:

.. code-block:: yaml

   mosquitto__bridges:
     'mqtt-local':
       address: 'mqtt.{{ ansible_domain }}'
       topic:
         - 'raw both 2 remote/topic/ local/topic/'
         - 'condensed both 2 remote/topic/ local/topic/'
       bridge_cafile: '{{ mosquitto__client_cafile }}'
       bridge_certfile: '{{ mosquitto__client_certfile }}'
       bridge_keyfile: '{{ mosquitto__client_keyfile }}'
       bridge_tls_version: '{{ mosquitto__tls_version }}'


.. _mosquitto__ref_auth_anonymous:

mosquitto__auth_anonymous
-------------------------

This variable can be used to define Access Control List for anonymous Mosquitto
users. It can be either a string (with one entry), a YAML text block (with
multiple entries) or a YAML list with string entries.

Each entry should be in the form:

.. code-block:: none

   topic [read|write|readwrite] <topic>

The specified entries will be included at the top of the
:file:`/etc/mosquitto/acl` file, therefore will apply to all users that don't
provide an username/password, ie. anonymous users.

Examples
~~~~~~~~

Allow read-only access to the broker status topics for anonymous users:

.. code-block:: yaml

   mosquitto__auth_anonymous:
     - 'topic read $SYS/#'


.. _mosquitto__ref_auth_users:

mosquitto__auth_users
---------------------

The :envvar:`mosquitto__auth_users`, :envvar:`mosquitto__auth_group_users` and
:envvar:`mosquitto__auth_host_users` can be used to configure user accounts in
Mosquitto. Each variable is a YAML list with entries specified as strings which
should be th user account names, or as YAML dictionaries that can be used to
control the user account configuration.

Batch password generation is supported on Mosquitto 1.4+, therefore
user/password entries will only work on older OS releases with upstream
Mosquitto, or Debian Stretch. On unsupported systems user accounts won't be
registered in the :file:`/etc/mosquitto/passwd` file, but they can be added or
removed manually using the :command:`mosquitto_passwd` command. The
``htpasswd`` Ansible module is not used here because it produces incompatible
hash strings.

The following parameters can be included in the YAML dictionary entries:

``name``
  Required: User account name.

``password``
  Optional. Password for a given user account. If not specified, a random
  password will be generated and stored in the :file:`secret/` directory in
  a subdirectory specified in the :envvar:`mosquitto__password_secret_path`
  variable. See :ref:`debops.secret` Ansible role documentation for more details.

``acl``
  Optional. Either a string, or a YAML list of entries to configure for a given
  user account. The format is the same as the anonymous ACL entries.

``state``
  Optional. If not specified or ``present``, the user account and its ACL
  entries will be configured on the host. If ``absent``, the user account entry
  and its ACL entries will be removed from the host.

Examples
~~~~~~~~

Create a ``roger`` user account with custom ACL entry:

.. code-block:: yaml

   mosquitto__auth_users:
     - name: 'roger'
       acl:  'topic foo/bar'


.. _mosquitto__ref_auth_patterns:

mosquitto__auth_patterns
------------------------

This variable can be used to define Access Control List based on topic
patterns. It can be either a string (with one entry), a YAML text block (with
multiple entries) or a YAML list with string entries.

Each entry should be in the form:

.. code-block:: none

   pattern [read|write|readwrite] <topic>

The topics can contain substitutions that are replaced by the broker:

- ``%c`` will match the client-id of a given client

- ``%u`` will match the username of the client

The specified entries will be included at the bottom of the
:file:`/etc/mosquitto/acl` file. The pattern ACLs apply to all users, even if
they have their own specific ACL entries.

Examples
~~~~~~~~

Allow per-user write access to a given topic:

.. code-block:: yaml

   mosquitto__auth_patterns:
     - 'pattern write sensor/%u/data'

Allow access to bridge connection data depending on the client id:

.. code-block:: yaml

   mosquitto__auth_patterns:
     - 'pattern write $SYS/broker/connection/%c/state'
