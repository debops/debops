.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`MinIO`__ is an Open Source Amazon Simple Storage Service (S3) compatible
object storage service.

.. __: https://min.io/

The ``debops.minio`` Ansible role can be used to deploy and configure MinIO in
various scenarios, either as a single node, single tenant service, or a multi
node and/or multi tenant distributed storage service. The role relies on other
DebOps roles to install MinIO binary from upstream URL or build it from source
code, configure firewall access, provide TLS support and configure web server
access to the service. See the Getting Started page for more details about the
deployment stack.

The `MinIO Client`__ application is used to interface with MinIO and perform
various administrative tasks, including extended configuration of the service.
It can be installed on a host using the :ref:`debops.mcli` Ansible role.

.. __: https://docs.min.io/docs/minio-client-complete-guide
