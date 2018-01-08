Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To configure the Preseed server, you can add a host to
``[debops_service_preseed]`` group::

    [debops_service_preseed]
    hostname

Default configuration will prepare Preseed files for Debian Wheezy and Debian
Jessie, which system administrator account named after either
``ansible_ssh_user`` or the username present on Ansible Controller host.

Example playbook
----------------

Here's an example playbook which uses ``debops.preseed`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/preseed.yml
   :language: yaml


How to use Debian Preseed configuration
---------------------------------------

``debops.preseed`` will use :ref:`debops.nginx` role to set up a webserver for the
Preseed files. They will be served on a separate subdomain, by default
``seed``. The FQDN given the ``example.org`` domain will be for example::

    debian.seed.example.org
    debian-vm.seed.example.org

You will need to define these subdomains in your DNS server, preferably as
a ``CNAME`` records pointed to the Preseed server.

If you have correctly configured DHCP server, which advertises your domain, you
will be able to access the Preseed configuration using a shorter form::

    debian.seed
    debian-vm.seed

The Debian Installer will automatically add your domain to the specified URL to get
the Preseed files.

To enable Preseeded installation, after starting the Debian Installer (tested
with Wheezy and Jessie),
navigate the menu to "Advanced options" -> "Automated Install".

Next, press the ``<Tab>`` key, this will let you enter additional boot options. Now
you can specify the URL of the Preseed file.

An example boot command line in Debian Installer::

    auto=true url=debian.seed hostname=<host>

After you press ``<Enter>``, the Debian Installer should start the installation
process. If you specified ``debian.seed`` as the Preseed file, the Debian Installer
should pause during the installation and let you configure the disk partitions
as you see fit. After configuring the partitions, the automatic installation will
resume and when it's finished the host will be automatically rebooted. After that
you should be able to SSH to it using the configured admin account.

The alternative Pressed configuration, ``debian-vm.seed`` is configured to
automatically partition and format the first hard drive with its full capacity,
without asking the user. This Preseed configuration is designed primary for
virtual machines, which usually have 1 partition stored in an image file or
a block device.

If you are not able to add `*.seed` to your DNS, you might use
:envvar:`preseed__base_domain` to make the server listen on a hostname
available via DNS. For this case the boot command line in Debian
Installer would require a different URL, like in this example (for
jessie)::

    auto url=<myhost>/debian/d-i/jessie hostname=<host>
