Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

On the first run of the ``debops.dhparam`` role, Ansible will generate a set of
Diffie-Hellman parameters (one or more, depending on what key sizes are
configured) and store them on the Ansible Controller, in ``secret/`` directory
managed by the :ref:`debops.secret` role. This set of DH parameters will be used to
"preseed" the remote hosts during initial Ansible playbook run to make
configuration of new hosts faster without the need to wait for new DH
parameters to be generated, which might take some time.

If ``atd`` service is installed and configured on the remote host (using
the :ref:`debops.atd` role), and parameter initialization is enabled, the role on first
run will create a batch job which will regenerate the DH parameters on the
remote hosts to make them unique. This will be done in the background with
lower process priority to minimize impact on the host performance. This way,
the preseeded DH parameters can be used right away, and when new parameters are
ready, they will automatically replace the preseeded ones.

Periodically (by default monthly) DH generator script will be run again, to
regenerate the DH parameters – this can be disabled as well if needed.

Configuration of DH parameters in applications
----------------------------------------------

Diffie-Hellman parameters managed by ``debops.dhparam`` can be found in
the :file:`/etc/pki/dhparam/` directory. By default, the role creates one set of parameters,
``set0`` with ``3072`` bit parameter length. You can increase the number of
sets, to use different DH parameters in different applications – each one will
be automatically preseeded by the pre-generated parameters, and managed by
regeneration script.

An example usage in a :program:`nginx` configuration file:

.. code-block:: yaml

   # Configuration in nginx server using a symlink
   ssl_dhparam /etc/pki/dhparam/set0

   # Configuration in nginx using the DH parameters directly
   ssl_dhparam /etc/pki/dhparam/params/set0/dh3072.pem

Use of DH parameters in Ansible roles
-------------------------------------

To make the Ansible configuration portable, ``debops.dhparam`` creates a set of
Ansible local facts which can be used by other roles to get the path to DH
parameters correctly using Ansible variables. These facts can be found in
``ansible_local.dhparam.*`` dictionary and can be used by other roles as:

.. code-block:: yaml

   # Specify the absolute path to the DH parameters
   role__dhparam: '{{ (ansible_local.dhparam[role__dhparam_set]
                       if (ansible_local|d() and ansible_local.dhparam|d() and
                           ansible_local.dhparam[role__dhparam_set]|d())
                      else "") }}'

   # Specify default parameter set to use
   role__dhparam_set: 'default'

Those two variables allow to easily change the default set of DH parameters to
a different one, or specify the path to DH parameters file directly. The
``d()`` pattern in the first variable is a short version of ``default()`` Jinja
filter and ensures that if the ``debops.dhparam`` role was not configured, Ansible
will not stop execution and instead will template an empty ``role_dhparam``
variable which this role can check and disable DH parameter support if necessary.

Because the configuration is passed using local Ansible facts,
``debops.dhparam`` role doesn't need to be used as a role dependency.

If any special operations have to be done when DH parameters file is replaced,
you can create scripts in :file:`/etc/pki/dhparam/hooks.d/` directory
(or ``'{{ ansible_local.dhparam.hooks }}'``). These hooks will be executed
using the ``run-parts`` command after all DH parameters have been regenerated.

Example inventory
-----------------

In DebOps, the ``debops.dhparam`` role is included in the :file:`common.yml` playbook and
is run automatically on all of the managed hosts. You don't need to
specifically enable it in Ansible's inventory.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.dhparam`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/dhparam.yml
   :language: yaml
