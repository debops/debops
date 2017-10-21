Default variable details
========================

Some of ``debops.redis`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _redis__ref_server_configuration:

redis__server_configuration
---------------------------

The Redis Server and Sentinel configuration is represented by a YAML
dictionary. Each key of this dictionary is a parameter name, and each value is
that parameter value.

The parameter values can be normal strings, integers, ``True`` and ``False``
booleans, or lists which are joined together with a space separator. If a value
is empty, that parameter will not be present in the generated configuration
file.

The role provides multiple variables which can be used on different inventory
levels for better control over Redis parameters. The
:envvar:`redis__server_combined_configuration` for Redis Server, and
:envvar:`redis__sentinel_combined_configuration` for Redis Sentinel combine these
YAML dictionaries together and determine the order in which variables "mask"
the previous parameters.

Consult the Redis example configuration files to see supported parameters and
their values.


.. _redis__ref_sentinel_monitors:

redis__sentinel_monitors
------------------------

This is the list of Redis master servers which the Redis Sentinel cluster
should monitor. Each entry is a YAML dictionary that describes the
configuration of a particular "monitor". The important parameters that
configure a Sentinel monitor are:

``name``
  Required. Name of the Redis Sentinel monitor to use. It should be short and
  it should only contain alphanumeric characters, as well as ``-_.``
  punctuation.

``host``
  Required. The DNS hostname or IP address of the Redis master server to
  monitor.

``port``
  Required. The TCP port on which the Redis master server listens for connections.

``quorum``
  Required. Number of Redis Sentinel instances in the cluster which are
  required to maintain a quorum.

Other parameters specified in a given monitor entry will be treated as that
monitor parameters and parsed accordingly. See the Redis Sentinel example
configuration file for their documentation.
