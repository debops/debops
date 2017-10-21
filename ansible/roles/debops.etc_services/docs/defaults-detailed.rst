Default variable details
========================

Some of ``debops.etc_services`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _etc_services__ref_list:

etc_services__list
------------------

The ``etc_services__*_list`` list variables allow you to generate entries for
local services not included in the officially distributed :file:`/etc/services`
file. They will generate separate files for each configured service in
:file:`/etc/services.d/` which then will be assembled into the
:file:`/etc/services` file.

Each list entry is a YAML dictionary with specific parameters:

``name``
  String, required. Name of the service, should be short and unique.

``port``
  String, required. TCP or UDP ort used by the service.

``protocols``
  List of strings, optional. Transport layer protocols of the service
  corresponding with ``port``.
  Common choices: ``tcp``, ``udp``.

``comment``
  String, optional. Comment to add to the service entry.

``filename``
  String, optional. Use this filename instead of a generated one.

``custom``
  String, optional. Specify custom file contents instead of templated one. If
  it is used, options like ``name`` and ``port`` are ignored.

``state``
  Either ``present`` or ``absent``. If it's defined and ``absent``, the local
  service configuration will be removed.

``delete``
  Boolean, optional, defaults to False. Delete the given local service.

Examples
~~~~~~~~

Create an entry for a custom TCP and UDP service:

.. code-block:: yaml

   etc_services__list:

     - name: 'servicename'
       port: '12345'
       protocols: [ 'tcp', 'udp' ]
       comment: 'Example service'
