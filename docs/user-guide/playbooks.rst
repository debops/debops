.. Copyright (C) 2015-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2015-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _playbooks:

Playbooks
=========

The DebOps Collection includes a set of Ansible playbooks pre-written for
convenience. Below you will find more details about them and their usage within
and outside DebOps.


How Ansible roles and playbooks work together
---------------------------------------------

Just to recap: Ansible uses modules to perform tasks on hosts, these tasks can
be combined into "playbooks" for greater functionality (variables, ability to
get facts about hosts, easier repeated use, assigning playbooks to specific
hosts or host groups). The contents of playbooks (list of tasks, variables,
files and templates) can be further extracted into "roles" to allow even more
flexibility and ability to use parts of the codebase in multiple places (the
`Don't Repeat Yourself`__ or "DRY" [*]_ principle).

.. __: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself

The roles are not usable on their own - Ansible can execute a role using the
``import_role`` module, but it won't be very useful, for example Ansible will
not have any facts about that host. The playbook still needs to be present, to
define a host-role relationship in larger environments, to join multiple roles
together into usable services (for example a firewall role and webserver role
working together to configure a HTTP service). Therefore to make things easier,
playbooks for DebOps roles are provided with the project itself.

You can find more about Ansible playbooks themselves in the `official
documentation`__.

.. __: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html


Default set of playbooks in DebOps
----------------------------------

The default playbooks provided in DebOps try to create an fairly typical Debian
or Ubuntu deployment. There's a set of common services expected to be
configured everywhere; some of them have exceptions for specific cases like
virtual machines or containers. The playbooks included in the project are not
supposed to be modified; users can create their own playbooks if needed.

Location of playbooks in the system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Easy way of browsing playbooks is using the `GitHub web interface`__. The link
points to the ``master`` :command:`git` branch, but you can select your
preferred tag or branch if needed.

.. __: https://github.com/debops/debops/tree/master/ansible/playbooks

Playbooks can be found in different locations depending on the installation
method. In the DebOps :command:`git` repository, playbooks are located in the
:file:`ansible/playbooks/` subdirectory. In the Python package (if installed on
the UNIX user account), they can be found at
:file:`~/.local/lib/python3.9/site-packages/debops/_data/ansible/collections/ansible_collections/debops/debops/playbooks/`
path (the Python version might differ). If DebOps was installed using Ansible
Galaxy collection, playbooks will be located in the :file:`debops.debops`
collection, under the :file:`playbooks/` directory.

The directory structure will look similar to this:

.. code-block:: console

   user@host:~/src/debops$ tree -L 2 ansible/playbooks
   ansible/playbooks/
   ├── bootstrap-ldap.yml
   ├── bootstrap-sss.yml
   ├── bootstrap.yml
   ├── common.yml
   ├── COPYRIGHT
   ├── layer/
   │   ├── agent.yml
   │   ├── app.yml
   │   ├── common.yml
   │   ├── env.yml
   │   ├── hw.yml
   │   ├── net.yml
   │   ├── srv.yml
   │   ├── sys.yml
   │   └── virt.yml
   ├── ldap/
   │   ├── get-uuid.yml
   │   ├── init-directory.yml
   │   └── save-credential.yml
   ├── reboot.yml
   ├── service/
   │   ├── ansible.yml
   │   ├── apache.yml
   │   ├── ...
   │   ├── yadm.yml
   │   └── zabbix_agent.yml
   ├── site.yml
   ├── templates/
   │   └── debops__tpl_macros.j2
   ├── tools/
   │   ├── 6to4.yml
   │   ├── debug.yml
   │   └── dist-upgrade.yml
   └── upgrade.yml

All of the :file:`*.yml` files are the playbooks. The :file:`site.yml` is the
"main entry point" where most of the playbooks are included. One of the
playbooks included is the :file:`layer/common.yml` playbook, which includes a
set of roles used on most of the hosts managed by DebOps (you can use it via a
shortcut, :file:`common.yml`, provided for backwards compatibility with older
DebOps releases).

Playbooks and Ansible inventory groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each playbook defines an Ansible inventory group on which it will be applied.
The ``[debops_all_hosts]`` inventory group is used in the
:file:`layer/common.yml` playbook, as well as all service playbooks of the
roles that are included in the common set. Each playbook in the
:file:`service/` subdirectory defines its own inventory group,
``[debops_service_<name>]`` which can be used to activate that specific
service. This way, users can execute the :file:`site.yml` playbook after
selecting which services should be configured on which hosts using Ansible
inventory groups. On the other hand, since each service has a corresponding
playbook, it can be executed directly to narrow the scope of the current
Ansible run.

DebOps services are organized into layers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Due to a large number of services managed by DebOps, they are organized in
"layers", for example services which configure hardware directly, system
services, networking, virtualization and so on. The playbooks are executed
sequentially in order of appearance, so the layer order is important. Main
order of layers is defined in the :file:`site.yml` playbook, but if needed,
each layer can be executed in the order specified by the user.

Check the playbooks in the :file:`ansible/playbooks/layer/` directory to see
order of execution of specific services.

.. note:: This setup applies since DebOps v3.1.0, older releases use a set of
          symlinks to achieve a similar result.


How to use provided playbooks with Ansible directly
---------------------------------------------------

An example Ansible inventory which can be used with this set of playbooks to
configure a :command:`nginx` webserver:

.. code-block:: none

   # ansible/inventory/hosts

   [debops_all_hosts]
   webserver    ansible_host=server.example.org

   [debops_service_nginx]
   webserver

You can apply a specific playbook using the :command:`ansible-playbook` command
by specifying it directly. For example, with the cloned :command:`git`
repository in :file:`~/src/debops/`, you can run the command:

.. code-block:: console

   $ ansible-playbook ~/src/debops/ansible/playbooks/site.yml

This will apply the :file:`layer/common.yml` playbook as well as the
:file:`service/nginx.yml` playbook. Since all project playbooks are involved,
execution might be a little slow. To speed it up, you can execute specific
playbooks:

.. code-block:: console

   $ ansible-playbook ~/src/debops/ansible/playbooks/layer/common.yml \
                      ~/src/debops/ansible/playbooks/service/nginx.yml

If DebOps collection has been installed from Ansible Galaxy, Ansible provides
a way to execute playbooks from the collection directly:

.. code-block:: console

   $ ansible-playbook debops.debops.site

   $ ansible-playbook debops.debops.layer.common \
                      debops.debops.service.nginx

The playbook syntax is ``<namespace>.<collection>.<playbook>`` with playbooks
located in subdirectories separated by a dot (``.``).


How to use playbooks via the :command:`debops` command
------------------------------------------------------

One of the reasons for the :command:`debops` scripts was to make it easier for
DebOps users to utilize the same set of Ansible playbooks in multiple
environments (project directories). :ref:`cmd_debops` knows how to parse the
list of short playbook names specified on the command line and find the
corresponding playbooks in different places - the ``debops.debops`` Ansible
Collection as a default, other Ansible Collections, the
:file:`ansible/playbooks/` subdirectory of the project directory.

The above examples when executed using the :command:`debops` script inside of
a DebOps project directory, would look something like this:

.. code-block:: console

   $ debops run site

   $ debops run layer/common service/nginx

As you can see, the syntax is a bit different - the :command:`debops` script
uses the slash (``/``) separator in the playbook paths. When slashes are found,
the script tries to resolve the path to a given playbook by itself. If dots are
used, the script passes the name of the playbook to Ansible so that the
:command:`ansible-playbook` can resolve the name using its internal mechanisms.
This means that specifying just the playbook names using dots won't work:

.. code-block:: console

   $ debops run layer.common
   ERROR! the playbook: layer.common could not be found

But if you specify the Ansible Collection in the playbook name, it will work
fine:

.. code-block:: console

   $ debops run debops.debops.layer.common

You can also specify the collection in playbook paths with slashes, so that the
:command:`debops` script will resolve the path to playbook, not
:command:`ansible-playbook`:

.. code-block:: console

   $ debops run debops.debops/layer/common

You can find more details about the :command:`debops run` and :command:`debops
check` commands syntax in the :ref:`debops run documentation <cmd_debops-run>`.


How to include DebOps playbooks in your own playbooks
-----------------------------------------------------

A common question among DebOps users is a way to include their own playbooks or
roles before or after DebOps playbooks. It's a bit tricky, since the official
playbooks are supposed to be read-only. On the other hand, Ansible doesn't have
a concept of "optional playbooks" - all playbooks specified in a given run,
either via the command line or imported into other playbooks, must exist before
Ansible execution can proceed. So in DebOps there's no way to provide some kind
of hooks where external playbooks can be plugged in later.

Let's create an exmaple playbook in the DebOps project directory,
:file:`ansible/playbooks/custom.yml`:

.. code-block:: yaml

   ---

   - name: Custom playbook
     hosts: 'debops_all_hosts'
     become: True

     tasks:
       - name: Message the user that we are in a custom playbook
         ansible.builtin.debug:
           msg: 'Hello from a custom playbook"

This playbook can be executed by the :command:`debops` script very easily:

.. code-block:: console

   $ debops run custom

The script will look in the :file:`ansible/playbooks/` project subdirectory,
where it will be found. Since users can specify multiple playbooks at once on
the command line, both the :file:`site.yml` playbook and the custom playbook
can be executed together, in either order:

.. code-block:: console

   $ debops run site custom

Another place where we can import DebOps playbooks is the custom playbook
itself, using the `ansible.builtin.import_playbook`__ Ansible module. The
playbook can be imported either before or after the custom "play", so we can
control the execution order.

.. __: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/import_playbook_module.html

For example, we can import the :file:`site.yml` playbook before our custom
tasks, so that DebOps codebase is executed first, mirroring the above example.
Here, we import a playbook from the cloned DebOps :command:`git` repository
(take note how the path to the user's home directory is expanded from the
``$HOME`` environment variable):

.. code-block:: yaml

   ---

   - name: Import DebOps playbooks
     ansible.builtin.import_playbook: '{{ lookup("env", "HOME")
                                          + "/src/debops/ansible/playbooks/site.yml" }}'

   - name: Custom playbook
     hosts: 'debops_all_hosts'
     become: True

     tasks:
       - name: Message the user that we are in a custom playbook
         ansible.builtin.debug:
           msg: 'Hello from a custom playbook"

If DebOps Collection has been installed from Ansible Galaxy, or the Python
package has been installed, the playbooks can be referenced using the Fully
Qualified Collection Name of the playbook:

.. code-block:: yaml

   ---

   - name: Import DebOps playbooks
     ansible.builtin.import_playbook: 'debops.debops.site'

   - name: Custom playbook
     hosts: 'debops_all_hosts'
     become: True

     tasks:
       - name: Message the user that we are in a custom playbook
         ansible.builtin.debug:
           msg: 'Hello from a custom playbook"

This way the custom playbook is a lot more portable and doesn't depend on the
location of the imported playbooks in the filesystem.

The above examples focus on using the :file:`site.yml` "entry point" playbook,
but this doesn't have to be the only one playbook that can be imported. Any
playbook in the DebOps collection can be imported either by referencing it in
the filesystem, or through its FQCN - for example, users can import the
``debops.debops.layer.common`` playbook to have only the common roles included
in their custom playbooks. For more flexibility, the :file:`site.yml` playbook
can be copied to the :file:`ansible/playbooks/` subdirectory in the DebOps
project directory and modified to import custom playbook at any point; just be
sure to not use the same name, and rename the playbook to, for example,
:file:`mysite.yml` so that the scripts can correctly find it.


.. rubric:: Footnotes

.. [*] Not named after drybjed.
