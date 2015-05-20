Default variables: configuration
================================

Some of ``debops.tinc`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _tinc_external_hosts:

tinc_external_hosts
-------------------

This is a dict variable which specifies the host name and configuration of
external VPN hosts which should be connected to the mesh network. Dict key
should be the hostname of the external host, dict value specifies the contents
of the host configuration file stored in
``/etc/tinc/<network>/hosts/<hostname>``. It should contain at least the list
of addresses on which connections can be made and RSA public key of the remote
host. Contents of the host file can be specified either as YAML text block, or
can be stored in a file accessed via ``lookup('file')`` plugin.

Examples:
~~~~~~~~~

Example external host configuration::

    tinc_external_hosts:

      'hostname': |
        Address = 10.10.99.128

        -----BEGIN RSA PUBLIC KEY-----
        MIICCgKCAgEAzrxMnWk7KjS5YaGedXHfAFqcRTTeYM28d6uGpTDiel0Lgl3SjgFy
        3Xuf41/RgExm2bOAhK1vIcxZnkALxcwQiVYsfASINEG0P9S7KNK+WUZ6ArnJYn6U
        ...
        qZARwVnml+Sknx22NJFwgWzklUIK3j+/3Eudxzu9JkGVeE9EkhRNoel9TVgGf3kj
        -----END RSA PUBLIC KEY-----

