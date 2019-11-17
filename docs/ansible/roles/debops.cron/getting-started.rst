Getting started
===============

.. contents::
   :local:


Randomized system jobs
----------------------

The role modifies the :file:`/etc/crontab` configuration file to randomize
execution times of ``hourly``, ``daily``, ``weekly`` and ``monthly``
:command:`cron` jobs. This is done to avoid huge spikes of job execution every
day around 06:25 which is the default execution time defined in the Debian and
Ubuntu ``cron`` package. The randomization is defined with the following rules:

- Each type of :command:`cron` job will have randomized minute at which the
  jobs will be executed.

- On each host, the role will choose the hourly execution time either at night
  (0-6) or in the evening (18-23). From that range, a specific hour will be
  chosen for each of the ``daily``, ``weekly`` and ``monthly`` jobs. This can
  be controlled using the :envvar:`cron__crontab_hour_ranges_map` variable.

- The ``weekly`` :command:`cron` jobs will be executed on either Saturday or
  Sunday, chosen randomly. you can specify what days to choose from using the
  :envvar:`cron__crontab_weekday_days` variable.

- The ``monthly`` :command:`cron` jobs will be executed on a randomized day of
  the first week of a month. This is controlled by the
  :envvar:`cron__crontab_day_ranges` variable.

The randomization is based on the :envvar:`cron__crontab_seed` variable (by
default uses the value of the ``inventory_hostname`` Ansible fact), as well as
some additional pseudo-random strings defined in the
:envvar:`cron__crontab_offset_seeds` list. The selected random values should be
stable across multiple :ref:`debops.cron` role executions, but may change
occasionally when other host configuration is changed.


Example inventory
-----------------

``debops.cron`` is included by default in the :file:`common.yml` DebOps playbook;
you don't need to do anything to have it executed.

If you don’t want to let ``debops.cron`` manage the :program:`cron` jobs, you
can do this with the following setting in your inventory:

.. code-block:: yaml

   cron__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.cron`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/cron.yml
   :language: yaml
