.. _gunicorn__ref_virtualenv_support:

Support for virtualenv environments
===================================

The role can be used to run WSGI applications deployed in a `virtualenv <http://virtualenv.org/>`_
environment. To do this, you need to install a ``gunicorn`` Python module
inside the environment at the same version as the Debian package. Below you can
find instructions for doing that with Ansible.

The ``debops.gunicorn`` role deploys an Ansible local facts script which
returns the version of the system ``gunicorn`` package. This fact can be
accessed as:

.. code-block:: yaml

   ansible_local.gunicorn.version

In your role, you can define a YAML list which specifies what Python modules
should be present in the ``virtualenv`` environment:

.. code-block:: yaml

   ---

   application__virtualenv_pip_packages:

     # Install compatible 'gunicorn' module inside the virtualenv
     - name: 'gunicorn'
       version: '{{ ansible_local.gunicorn.version
                    if (ansible_local|d() and ansible_local.gunicorn|d() and
                        ansible_local.gunicorn.version|d())
                    else omit }}'

     # Install 'setproctitle' for nice process names
     - 'setproctitle'

Next, in your role task list, include set of tasks that will create the
``virtualenv`` environment and install the required modules inside (the example
below requires Ansible 2.1+ to work):

.. code-block:: yaml

   ---

   - name: Create the virtualenv environment
     pip:
       name: 'wsgiref'
       virtualenv: '/path/to/virtualenv'
     become_user: 'app-user'

   - name: Install additional Python modules for gunicorn support
     pip:
       name:    '{{ item.name    | d(item) }}'
       version: '{{ item.version | d(omit) }}'
       virtualenv: '/path/to/virtualenv'
     with_flattened: '{{ application__virtualenv_pip_packages }}'
     become_user: 'app-user'

The above tasks can be combined into one if you don't need to perform
additional steps between creating the environment and installing additional
modules.

The above steps should ensure that the application deployed in the
``virtualenv`` environment can be started by the ``gunicorn`` service installed
from the Debian packages. To do that, you can define the application using the
role dependent variables in your role's :file:`defaults/main.yml` file, like this:

.. code-block:: yaml

   ---

   application__gunicorn__dependent_applications:

     - name: 'virtualenv-app'
       working_dir: '/path/to/virtualenv/app/src'
       python: '/path/to/virtualenv/bin/python'
       mode: 'wsgi'
       user: 'app-user'
       group: 'app-group'
       args: [ '--bind=unix:/run/gunicorn/virtualenv-app.sock',
               '--workers={{ ansible_processor_vcpus|int + 1 }}',
               '--timeout=10' 'virtualenv-app.wsgi' ]

And the corresponding playbook which uses ``debops.gunicorn`` as a dependent
role:

.. code-block:: yaml

   ---

   - name: Deploy the application
     hosts: [ 'application-hosts' ]
     become: True

     roles:

       - role: debops.gunicorn
         gunicorn__dependent_applications:
           - '{{ application__gunicorn__dependent_applications }}'

       - role: application-role

Currently there's no way to request that the ``gunicorn`` service should be
restarted apart from specifying the ``Restart gunicorn`` Ansible handler
directly in your role, for example like this:

.. code-block:: yaml

   ---

   - name: Generate the application configuration
     template:
       src: 'path/to/virtualenv/app/src/config.j2'
       dest: '/path/to/virtualenv/app/src/config.j2'
       owner: 'app-user'
       group: 'app-group'
       mode: '0644'
     notify: [ 'Restart gunicorn' ]

This requires that the ``debops.gunicorn`` role is included in the playbook
that manages your application. This restriction will be changed in the future,
when Ansible handlers will be able to listen for notifications.
