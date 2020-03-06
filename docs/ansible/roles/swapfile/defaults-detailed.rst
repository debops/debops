.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
================================

Some of ``debops.swapfile`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _swapfile__files:

swapfile__files
---------------

``debops.swapfile`` can manage multiple swap files at once. This list in
a simple form specifies absolute filenames of the swap files to manage.

An extended configuration can be done using a YAML dictionary for each swap
file. List of recognized parameters:

``path``
  Required. Path of the swap file to manage.

``size``
  Optional. Set the size in MB of a given swap file.

``priority``
  Optional. Specify a priority of the swap file.

``state``
  Optional. If specified and ``absent``, swap file will be disabled and deleted
  from the system.

Examples
~~~~~~~~

Manage two swap files at once:

.. code-block:: yaml

   swapfile__files:

     - '/swapfile0'

     - path: /swapfile1'
       size: '1024'
