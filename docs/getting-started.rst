Getting started
===============

.. contents::
   :local:

Main issue with RStudio Server installation is lack of convenient Debian/Ubuntu
APT repositories and dependency on ``libssl0.9.8`` package, only available in
Debian Squeeze release, which is supported through Debian LTS project.

In contrast to this, ``debops.rstudio_server`` installs the packages through
APT, without downloading them directly from upstream servers. You can install
these packages either manually using ``dpkg``, or add them to a local APT
repository managed by ``debops.reprepro`` role (or other similar service).

Get the required packages
-------------------------

You need to download the packages listed below to Ansible Controller, or other
host where they can be accessed. If you want, you can at this point add them to
``reprepro`` repository using ``includedeb`` option. Otherwise, you can install
these packages manually on the remote host after running the role (see below).

``rstudio-server``
  RStudio Server package can be downloaded from the official `RStudio website
  <http://www.rstudio.com/products/rstudio/download-server/>`_. You should pick
  the package for your architecture, usually it's 64bit / amd64.

``libssl0.9.8``
  Required libssl package can be downloaded from `packages.debian.org
  <https://packages.debian.org/libssl0.9.8>`_. You most certainly want latest
  ``squeeze-lts`` version of the package which is the only one currently
  supported.

Example inventory
-----------------

To configure a host for RStudio Server, it needs to be in the
``[debops_rstudio_server]`` Ansible group::

    [debops_rstudio_server]
    hostname

You can run the role without the external packages present,
``debops.rstudio_server`` will check if they are available and won't configure
RStudio itself, however the ``nginx`` webserver and R environment will be
installed.

Example playbook
----------------

Here's an example playbook which uses ``debops.rstudio_server`` role::

    ---

    - name: Install RStudio Server
      hosts: debops_rstudio_server

      roles:
        - role: debops.rstudio_server
          tags: rstudio_server

Manual package installation
---------------------------

If you did not add the external packages to a local APT repository, you will
need to install them manually. Copy the ``*.deb`` packages you downloaded to
the remote host and install them using ``dpkg`` command::

    scp path/to/*.deb remote-host:
    ssh remote-host
    sudo dpkg -i *.deb

After the packages have been installed, and before you re-run the
``debops.rstudio_server`` role, stop the ``rstudio-server`` service so that it
can be reconfigured. on Debian Wheezy or systems with ``sysvinit`` or
``upstart``, you can do that by running command::

    sudo service rstudio-server stop

On Debian Jessie and other hosts with ``systemd``, you do this by running
command::

    sudo systemctl stop rstudio-server.service

Next, re-run the ``debops.rstudio_server`` role. It will reconfigure the
application to be accessible through the webserver and start it automatically.

