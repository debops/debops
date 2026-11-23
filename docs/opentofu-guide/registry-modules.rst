.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _tofu_registry_modules:

OpenTofu modules on a GitLab registry
=====================================

.. contents::
   :local:

OpenTofu modules are reusable units of infrastructure, and a private
registry keeps them under your control instead of a public account's.
GitLab hosts Terraform/OpenTofu modules per namespace, in the Free
tier of the CE build. OpenTofu resolves the module source through the
host's discovery document and downloads the archive authenticated.
Modules have no lock file -- the ``version`` constraint of each module
source is the pin. Record exact versions.


Publishing
----------

Pack the module and upload it to a project of the target group:

.. code-block:: console

   alice@controller:~$ tar -C ~/src/modules/probe-module \
       -czf probe-module.tar.gz main.tf
   alice@controller:~$ curl -sS -H "PRIVATE-TOKEN: <token>" \
       --upload-file probe-module.tar.gz \
       "https://gitlab.example.com/api/v4/projects/42/packages/terraform/modules/probe-module/system/1.0.0/file"

Two details of the publish route:

- The publish URL ends in :literal:`/file`. Without it the route does
  not exist and the API answers with the generic route-miss 404.
- The publish authenticates with the ``PRIVATE-TOKEN`` header.
  The consumption half of the same registry wants
  :literal:`Authorization: Bearer` and rejects ``PRIVATE-TOKEN``.
  The two halves want different headers. The credentials block below
  sends the right one for the downloads.

The registry serves modules at the group level: the module published
to a project appears under
:literal:`/api/v4/packages/terraform/modules/v1/<group>/<module-name>/<system>`,
regardless of the project name.


Consuming from a DebOps view
----------------------------

The controller's :file:`~/.tofurc` carries the credentials OpenTofu
sends as the Bearer header for the registry protocol. The file is per
controller, mode 0600, one credentials block per host:

.. code-block:: text

   # ~/.tofurc
   credentials "gitlab.example.com" {
     token = "<personal access token>"
   }

Record the module in the view's configuration drop-in. The source is
the registry address in the OpenTofu notation. The local name derives
from the third segment:

.. code-block:: console

   alice@controller:~$ debops config set views.<view>.tofu.modules \
       '{"probe-module": {"source": "gitlab.example.com/<group>/probe-module/system", "version": "1.0.0"}}'
   alice@controller:~$ debops tofu -V <view> update

The same record, written by hand in the view's configuration drop-in:

.. code-block:: toml

   # .debops/conf.d/view-<view>-tofu.toml

   [views."<view>".tofu.modules.probe-module]
   source = "gitlab.example.com/<group>/probe-module/system"
   version = "1.0.0"

The recorded set lives wherever you place it: the drop-in which
the view creation wrote, or the file the :command:`config set`
command manages. The update renders the same :file:`modules.tf`
from the merged configuration tree.

The update regenerates the view's :file:`modules.tf` from the
recorded set. The init downloads the module through the registry,
authenticated, into the relocated data directory. The view tree
carries no module cache.

The plan then surfaces the module's resources under the
``module.<local-name>.`` prefix, and the apply lands them in the
state -- remote or local alike.

The scheme-prefixed and local-path sources do not go through the
:literal:`-m/--module` options: the options record registry modules,
whose local name the source address derives. Instantiate a
:literal:`git::` or :literal:`oci://` module in the view
configuration drop-in directly, keyed by the local name you choose.


Inputs and versions
-------------------

The drop-in records the module inputs beside the source, and the
generated :file:`modules.tf` renders them as HCL:

.. code-block:: console

   alice@controller:~$ debops config set views.<view>.tofu.modules '{"probe-module": {"source": "gitlab.example.com/<group>/probe-module/system", "version": "1.0.0", "inputs": {"environment": "production", "gateway_address": "hcl:incus_instance.gateway.ipv4_address", "plain_note": "hcl:hcl:not an expression"}}}'

The same record, hand-written in the drop-in:

.. code-block:: toml

   # .debops/conf.d/view-<view>-tofu.toml

   [views."<view>".tofu.modules.probe-module]
   source = "gitlab.example.com/<group>/probe-module/system"
   version = "1.0.0"

   [views."<view>".tofu.modules.probe-module.inputs]
   environment     = "production"
   gateway_address = "hcl:incus_instance.gateway.ipv4_address"
   plain_note      = "hcl:hcl:not an expression"

The update renders the module block of :file:`tofu/views/<view>/modules.tf`:

.. code-block:: text

   module "probe-module" {
     source  = "gitlab.example.com/<group>/probe-module/system"
     version = "1.0.0"

     environment     = "production"
     gateway_address = incus_instance.gateway.ipv4_address
     plain_note      = "hcl:not an expression"
   }

Plain values render as their HCL equivalents, the quoting
included. A string value prefixed with :literal:`hcl:` carries a
raw HCL expression. The bridge consumes the prefix once, and the
rest lands in the generated file verbatim. The
``gateway_address`` above is how a module input receives a
reference to another resource instead of a literal. A value which
carries the prefix twice is the escaped literal: ``plain_note``
renders as the string :literal:`hcl:not an expression`. An empty
expression after the prefix refuses the render.

Bump the recorded version and run :command:`debops tofu -V <view>
update -upgrade` when the module moves. OpenTofu re-resolves the
module on the next init. The view tree never holds a stale copy.


See also
--------

- :ref:`debops_tofu` for the OpenTofu integration and the module
  options
- :ref:`tofu_remote_state` for the remote state on the same GitLab
  instance
