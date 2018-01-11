Using Linux containers
======================

- `Host requirements`_
- `Configuring a host`_ to make it capable of storing containers
- `LXC cheatsheet`_ to help you manage the containers
- `Interacting with a container`_

Host requirements
-----------------

**Your host must be Debian based.**

Debian stable and oldstable are supported by DebOps, as well as the two latest
LTS releases of Ubuntu. However the main focus will always be towards the
latest Debian Stable followed by the latest Ubuntu LTS release. So if you plan
on setting up a new machine, always use the latest OS release.

If you're using a Mac or a different Linux distro then you'll want to setup a
virtual machine to act as the container host. You can do this with
`Vagrant <https://www.vagrantup.com/>`_ or some other virtualization software.

**SSH key pair**

You will also need an SSH key pair on your host. You probably have one setup,
but if you don’t, you can run ``ssh-keygen -t`` and follow the instructions.
DebOps expects the SSH keys to be in ``~/.ssh``.

Configuring a host
------------------

**Adding it to your inventory**

The paths are relative to where you ``debops-init`` a new project.

:command:`ansible/inventory/hosts`

::

    [debops_service_lxc]
    yourhostname

**Decide on which network adapter you're using**

If you plan to make your main OS an LXC host then you'll want to configure the
host to use the NAT adapter by default. DNS is configured through NAT using
dnsmasq.

Basically this means you don't have to forward ports and DNS will work.

:file:`ansible/inventory/host_vars/yourhostname.yml`

::

    lxc_configuration_default: 'nat'

If you plan to use the bridged adapter through a VM then you do not have to set
anything but keep in mind you will need to connect through an IP address unless
you have configured DNS yourself.

**Make the host an LXC host by running DebOps**

Run this from your terminal: ``debops -l debops_service_lxc``.

If you are running Debian Wheezy you will have to reboot your LXC host due to
a kernel update. Later Debian releases and all supported Ubuntu releases do not
require a reboot.

LXC cheatsheet
--------------

::

    # Create a new container
    sudo lxc-create -n mycontainer -t debops

    # Return back a list of containers and basic information about them
    sudo lxc-ls -f

    # Start a container, the -d flag runs it as a daemon
    sudo lxc-start -n mycontainer -d

    # Stop a container
    sudo lxc-stop -n mycontainer

    # Destroy a container, the -f flag does a stop before destroying it
    sudo lxc-destroy -n mycontainer -f

    # There are many more commands like snapshotting, freezing, info, etc.
    # Check the LXC manpages for more information
    sudo lxc-[tab complete]

Interacting with a container
----------------------------

Once it has been created and it's running you can SSH to it, just run:

``ssh containername`` if you have DNS setup, otherwise use the IP address. At
this point you have a bare container ready to do whatever you want.

**Setting it up with common DebOps services**

If you plan to use containers for development then you'll probably want
to group your containers together in your inventory.

:command:`ansible/inventory/hosts`

::

    [local_containers]
    mycontainer

Now you could create :file:`ansible/inventory/group_vars/local_containers.yml` and
start doing things that would apply to all local containers.

Perhaps you want to install emacs or use your own dotfiles, etc..

**Transferring files**

To transfer files to/from the container you have 2 options.

1. SCP or some other file transfer utility that works through SSH

::

    # To the container
    scp somefile mycontainer:/tmp/somefile

    # From a container
    scp mycontainer:/tmp/somefile somefile

The second option requires knowing the dirty details about where the container
has its configuration and file system stored.

On the LXC host, navigate to :file:`/var/lib/lxc`, then go into your container's
directory. You can find its file system there among other things. You can simply
``cp`` directly if your LXC host is local to your main OS.
