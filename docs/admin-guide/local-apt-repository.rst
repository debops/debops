Creating a local apt server
===========================

- `What are some benefits of doing it this way?`_
- `Picking a host for the repository`_
- `Configuring a throw away build server`_
- `Configuring the local APT server`_
- `Making your hosts aware`_
- `Using your shiny new package`_

Certain roles such as Ruby and Golang offer the ability to use a backported
version of the package so it's more up to date. The backports are built off of
Debian testing without having to actually use the testing apt source.

What are some benefits of doing it this way?
--------------------------------------------

A lot of other roles will compile from source  but that's time demanding and
error prone. A backported version of Ruby 2.1.x will apt install in about 5
seconds once you setup your local APT server once.

.. note::
    Compile it once into a proper package and use it as many times as you want.

It also makes your role future proof because you don't have to change anything
once the next Debian version is officially released. From the role's point of view it's just
installing an apt package using Ansible's :command:`apt` module. It does not care where
the apt server is located.

Picking a host for the repository
---------------------------------

The first step is to decide where you want this server. It doesn't need to be
literally local to your workstation. It's local in the context of it not being
an official APT server to the world.

Popular options could be your Ansible controller inside of a container or a
micro-size instance on the cloud depending on your requirements for availability.

Configuring a throw away build server
-------------------------------------

You could use your apt server but it's best to use a temporary host. I would
just spin up a container.

In this example we're going to build Ruby 2.1.x. You will have to do this if
you plan to use GitLab so it's a good idea to learn!

::

  # inventory/hosts

  [debops_service_ruby]
  yourbuildserver

::

  # inventory/host_vars/yourbuildserver.yml

  ruby_version: 'backport'

That tells the `Ruby role <https://github.com/debops/ansible-ruby>`_ to use
the `Backporter role <https://github.com/debops/ansible-backporter>`_ as a
dependency and that will kick off the entire build process for you.

**Then run:**

``debops -l yourbuildserver``

Expect it to take 5 to 15 minutes depending on how fast your server is. You only
need to do this once.

Where are the packages?
~~~~~~~~~~~~~~~~~~~~~~~

Good question, they have been transferred to your Ansible controller in the
:file:`secret/reprepro/includedeb/wheezy-backports/` directory.

At this point you can delete your build server.

Configuring the local APT server
--------------------------------

Next up, we need to tell our server that it is an APT server.

::

  # inventory/host_vars/youraptserver.yml

  apt: 'youraptserver.{{ ansible_domain }}'

You must use your apt server's fully qualified domain name. Run ``hostname -f`` on
the server to check its fully qualified domain name.

**We're just about done**, now you need to transfer the packages to your apt server:

``debops -l youraptserver -t apt``

Making your hosts aware
-----------------------

The last step is to make your hosts aware of the server.

Below I'm just assuming you want to make it aware to all of your containers and
you have your containers inside of a ``[containers]`` group.

::

    # inventory/group_vars/containers.yml

    apt: 'youraptserver.{{ ansible_domain }}'

**Then run:**

``debops -l containers``

Using your shiny new package
----------------------------

Well, this part is easy. Just use the Ruby role on any host that is aware of
your local apt server and it will install Ruby 2.1.x in about 5 seconds.

You do not need to set ``ruby_version: 'backport'`` on the hosts themselves. It
will just use the default setting which is the apt package and now since your
local apt server is setup and your host is aware, it will use the new backported
version.
