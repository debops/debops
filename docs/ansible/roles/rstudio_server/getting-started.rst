.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


.. _rstudio_server__ref_installation_issues:

Installation issues
-------------------

The RStudio Server is not available through an APT repository, upstream
releases a ``.deb`` package along with the sources. The role will check if the
``rstudio-server`` package is available through APT; otherwise the ``.deb``
package will be downloaded directly from the project's website and installed
using :command:`dpkg`. The package integrity is checked via SHA256 checksum. The
package can also be provided via a local APT repository if desired.


Example inventory
-----------------

To configure a host for RStudio Server, it needs to be in the
``[debops_service_rstudio_server]`` Ansible group:

.. code-block:: none

   # Optional Java support in R environment
   # See 'debops.cran' role for mode details
   [debops_service_java]
   hostname

   [debops_service_rstudio_server]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.rstudio_server`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/rstudio_server.yml
   :language: yaml
   :lines: 1,5-
