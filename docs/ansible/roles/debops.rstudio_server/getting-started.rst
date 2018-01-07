Getting started
===============

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

At present, the RStudio Server package prepared by upstream is compiled against
the OpenSSL 1.0.0 library provided by the ``libssl1.0.0`` package. This package
is included in Debian Jessie release, but it has been removed in Debian
Stretch; existing ``libssl1.0.2`` version doesn't seem to be correctly
recognized by RStudio Server. This means that the service can be correctly
installed on Debian Jessie, but not on Debian Stretch.

To overcome that limitation, on Debian Stretch systems the role downloads the
``libssl1.0.0`` package from Debian Jessie directly from the Debian Archives
and installs it using :command:`dpkg`. This allows for the RStudio Server to run
correctly, however the role's author doesn't guarantee that resulting system is
secure and without issues.

This arrangement is hopefully temporary, until RStudio releases a new version
of the package compiled against newer version of OpenSSL. As an alternative,
the users can compile their own version of RStudio Server ``.deb`` package
against Debian Stretch and provide it via local APT repositories, in that case
installation of ``libssl1.0.0`` package can be disabled via a boolean variable.


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
