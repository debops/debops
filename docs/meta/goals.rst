.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _goals:

Project goals
=============

The work on the DebOps project began around October 2013; some of the reasons
it was started might have been fixed over time, but there's still lots of
problems to work on. Here's a short list of issues we would like to solve
using this project.

This list is an objective look at the goals of the DebOps project. If you want
a more subjective, personal take on the project by its contributors, check the
:ref:`philosophy` page.

.. contents::
   :local:

Provide an universal configuration layer for Debian hosts and clusters
----------------------------------------------------------------------

`Debian`__ is an excellent base operating system to build your infrastructure
on. It focuses on stability, sane upgrade paths and provides a somewhat
consistent schedule for new releases. But there are also issues Debian
administrators need to deal with, one of which is system configuration and
policy enforcement. This issue is even more noticeable when we move from the
boundaries of local system administration and into a clustered environment with
multiple Debian machines which are meant to work together.

These problems exist partially due to the nature of the Linux ecosystem where
each piece of software comes with its own idea of configuration system (usually
files and directories in the :file:`/etc/` directory with different file
formats; some exceptions come with more esoteric solutions like configuration
stored in databases), and partially due to lack of an universal configuration
solution available in the past, which could take over the task of configuring
the installed software.

Some solutions were attempted previously, like proposal of a `Distributed Admin
Tool`__ with a sophisticated client-server architecture; unfortunately the
project seems to be abandoned, perhaps due to advent of various `configuration
management software`__ which would make the custom Debian application
redundant. A different solution used in Debian itself is `config packages`__
system which consists of creating ``.deb`` packages that can be installed using
the :command:`dpkg` package manager used in Debian and rely on various
facilities used in the distribution to modify or override configuration of
packaged software. This provides a clean way to deploy configuration in
a cluster of machines via the package management system, but is hard to use
effectively to create a generalized solution.

In recent years, configuration management ecosystems exploded in popularity.
The Debian Popularity Contest data for `Chef`__, `Ansible`__, `Puppet`__ and
`SaltStack`__ show that there's no need to invent a new configuration tool from
scratch anymore. All a system administrator needs is to express the
configuration of their environment using existing tools. This of course incurs
a large investment in time to research the applications we want to configure,
more time to learn the tool we want to use to maintain the configuration, and
so on. A way around this is to design the configuration infrastructure to be
generic, so that multiple organizations can benefit from the invested time and
customize the result according to their own needs.

This is where DebOps comes in. It's a set of Ansible playbooks and roles that
are designed to tightly integrate with the Debian ecosystem and work together
to configure and manage various services, both on the local system and on the
remote hosts in a cluster. DebOps roles leverage the operating system
facilities where possible to make the upgrade path easier; for example
configuration files are not overwritten directly where possible, but diverted
using :man:`dpkg-divert(1)` mechanism to preserve the configuration during
upgrades. When different services that need to work together don't provide any
mechanisms for integration, DebOps roles are used to mediate use of shared
resources (for example firewall or webserver configuration).

.. __: https://www.debian.org/
.. __: https://wiki.debian.org/DistributedAdminTool
.. __: https://en.wikipedia.org/wiki/Comparison_of_open-source_configuration_management_software
.. __: https://wiki.debian.org/ConfigPackages

.. __: https://qa.debian.org/popcon.php?package=chef
.. __: https://qa.debian.org/popcon.php?package=ansible
.. __: https://qa.debian.org/popcon.php?package=puppet
.. __: https://qa.debian.org/popcon.php?package=salt


Provide a consistent and well-intgrated set of roles for Ansible users
----------------------------------------------------------------------

`Ansible`__, started in 2012, is one of the most popular configuration
management tools currently available. Over the years it evolved from simple
orchestrator using SSH to execute commands on remote hosts to a complete
solution for configuration management and policy enforcement on multiple
platforms and with a `galaxy`__ of modules, roles and other elements of
a successful ecosystem.

One of the greatest strengths of Ansible is the design conductive for creation
of general-purpose configuration solutions – roles and playbooks can be
composed together to customize the result for the needs of an organization, the
variable and inventory system allows for even more ways to customize the roles
when they are written to take advantage of it. Configuration of distinct
services can affect each other conditionally, allowing for clear separation of
duties between Ansible roles which helps with their maintenance and upkeep.

In 2013, when project which eventually became DebOps started to take shape,
there weren't many publicly available solutions that provided system
administrators with ready-made set of Ansible roles and playbooks to configure
their environments. They usually focused on a specific set of goals for
deploying the infrastructure. Some examples of such projects are `Sovereign`__,
`Streisand`__ and `Algo VPN`__. These projects are usually self-contained and
are not designed for easy extensibility.

Over the years new solutions came along, which were more focused and easier to
extend as needed. Some examples include `Manala`__ and `DevSec`__ projects.
DebOps is yet another solution for configuration management now, although with
a few unique concepts and focus on general-purpose system configuration that
can be customized to the user's own needs.

.. __: https://en.wikipedia.org/wiki/Ansible_(software)
.. __: https://galaxy.ansible.com/

.. __: https://github.com/sovereign/sovereign
.. __: https://github.com/StreisandEffect/streisand
.. __: https://github.com/trailofbits/algo

.. __: http://www.manala.io/
.. __: https://dev-sec.io/


Offer a stable and extensible platform to build infrastrucure upon
------------------------------------------------------------------

Containers changed how we deploy complex systems. Where before setting up
a service meant installing base operating system, then required runtimes,
configuration of various services on local and remote hosts, then installation
of the application itself, now all of that can be neatly encapsulated in
a standardized container image which is then used by different execution
engines to manage application instances.

However, classical configuration management still has its place. In a cloud
environment which primarily uses containers as application delivery method,
configuration management tools can be used to create these images with required
configuration "baked-in" during the build process. In self-hosted or
on-premises environments, configuration management can be used to configure
hosts from scratch, including setting up hypervisors for virtual machines or
container environments which then can leverage the container-based deployments.

Configuration management best practices were developed over many years by
experienced system administrators. The current set of CM tools can be used to
easily capture that experience, share it with others and improve for the
benefit of the entire community.


Provide a set of building blocks for complex deployments
--------------------------------------------------------

Typical infrastructure deployments are composed of multiple services. There's
the base operating system which defines the environment; a firewall service
controls the access to other services; a webserver provides an access point to
the static and dynamic applications; database services create different storage
solutions available to the applications. Each of these services is usually
managed as standalone, but they are meant to work together to achieve a task.

The Ansible roles included in the DebOps project are meant to define a concise
and stable API surface between different services. Each role should focus on
specific service configuration and in turn, provide an interface for other
roles where appropriate so that multiple services can be configured together
without conflicts.

This will allow the project to provide a set of "stacks" written as Ansible
playbooks that use multiple Ansible roles together to deploy complex
applications - a WordPress blog, a VM hypervisor host, a container cluster will
be composed of the same set of building blocks, which allows creation of
customized environments, tailored for a particular organization.


Final goal: DebOps is used to set up a data center in an extraterrestrial colony
--------------------------------------------------------------------------------

Every project needs a final goal which, when reached, marks its completion. The
final goal of the DebOps project is for it to be used on an extraterrestrial
colony to set up a data center.

It's not a pipe dream. Debian has already made it into space, due to `being
used as the operating system on various laptops used on the International
Space Station`__. Humanity already made it to the Earth's Moon in the past, so
we will be getting there at some point in the future; other planets like Mars
will also be visited. Eventually a new human colony will be established,
either on a planetary/lunar surface, on an asteroid or within an artificial space
station. In such case, at least one local data center will have to be set up to
facilitate computing tasks optimally.

After basic life-form needs are met by things like life support systems, the
colony grows and more people show up to live and work there, a GNU/Linux-like
environment will become a necessity. Debian has a high chance of being selected
as the base operating system for such task, due to its wide range of supported
architectures and large software library which can be easily packaged and sent
into space to be available locally.

When that eventually happens, DebOps should be ready to assist the local system
administrators to set up and maintain their infrastructure. This of course
requires other things to happen - the project needs to be useful enough to be
recognized as a good choice for that purpose. Clean codebase, extensive
documentation, long-term planning and best practices used to facilitate its
operation will also help.

Let's get it done.

.. __: https://phys.org/news/2013-05-international-space-station-laptop-migration.html
