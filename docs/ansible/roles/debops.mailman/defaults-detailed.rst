Default variable details
========================

Some of ``debops.mailman`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _mailman__lists:

mailman__lists
--------------

Create or remove mailing lists. This is a simple interface to ``newlist`` and
``rmlist`` Mailman commands, not really intended for proper list management,
which should be performed through the web interface.

Each list is defined as a dictionary with following keys:

``name``
  Required. Name of the mailing list.

``domain``
  Optional. If specified, sets the domain of the mailing list. The domain
  should be configured as one of Mailman virtual domains.

``owner``
  Optional. Specify e-mail address of the mailing list owner. If not specified,
  site admin will be the owner of this mailing list.

``language``
  Optional. Specify the mailing list default language as two-letter name. The
  language pack should be enabled on the server. If not specified, the default
  site language will be used.

``password``
  Optional. Specify the mailing list owner password. If not specified, a random
  password will be generated automatically and stored in the ``secret/``
  directory (highly recommended). See the :ref:`debops.secret` role documentation
  for more details.

``state``
  Optional. If not specified, or specified and set to ``present``, the mailing
  list will be created. If set to ``absent``, it will be removed.

``purge``
  Optional, boolean. If specified and set to ``True``, the mailing list
  archives will be purged when the mailing list is removed.

Examples
~~~~~~~~

Create a new mailing lists:

.. code-block:: yaml

   mailman__lists:

     - name: 'project-users'

     - name: 'project-devel'
       language: 'en'
       owner: 'project-devel@example.org'
