.. _cron__ref_defaults_detailed:

Default variable details
========================

Some of ``debops.cron`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _cron__ref_crontab_jobs:

cron__crontab_jobs
------------------

The ``cron__crontab_*_jobs`` variables define what :command:`cron` jobs will be
present in the :file:`/etc/crontab` configuration file. You can read more about
the contents of this file in the :man:`crontab(5)` manual page.

This configuration is meant for the system-wide :command:`cron` configuration,
application-specific :command:`cron` jobs should be configured via the
:ref:`cron__ref_jobs` variables.

Examples
~~~~~~~~

The syntax is similar to that used by the `cron Ansible module`__.

.. __: https://docs.ansible.com/ansible/latest/modules/cron_module.html

Define a :command:`cron` job which will be executed every minute:

.. code-block:: yaml

   cron__crontab_jobs:
     - name: 'run-each-minute'
       job: '/bin/true'

Run a job each day at midnight:

.. code-block:: yaml

   cron__crontab_jobs:
     - name: 'run-each-day'
       minute: '0'
       hour: '0'
       job: '/bin/true'

Alternative way to run a job each day at midnight:

.. code-block:: yaml

   cron__crontab_jobs:
     - name: 'run-each-day'
       special_time: 'daily'
       job: '/bin/true'

Run a job as the ``nobody`` user, 23 minutes every two hours, every day:

.. code-block:: yaml

   cron__crontab_jobs:
     - name: 'custom-job-schedule'
       user: 'nobody'
       special_time: '23 0-23/2 * * *'
       job: '/bin/true'

You can also check the :envvar:`cron__crontab_default_jobs` variable to see the
configuration of the ``hourly``, ``daily``, ``weekly`` and ``monthly``
:command:`cron` job schedules.

Override daily :command:`cron` job schedule to execute on a specific hour
instead of the randomized one:

.. code-block:: yaml

   cron__crontab_jobs:
     - name: 'crontab-daily'
       hour: '5'

Syntax
~~~~~~

Each list entry is a YAML dictionary that describes a :command:`cron` job using
specific parameters:

``name``
  Required. A string that defines a configuration entry, not used otherwise.
  Configuration entries with the same ``name`` parameter are merged together in
  the order of appearance and can affect each other.

``job``
  Required. The command to execute by :command:`cron` for a given job.

``state``
  Optional. If not specified or ``present``, a given job will be included in
  the generated :file:`/etc/crontab` file. If ``absent``, a given job will be
  removed from the generated file. If ``ignore``, the configuration entry will
  not be evaluated by role during execution.

``minute``
  Optional. Execute a :command:`cron` job on a specific minute. If not
  specified, ``*`` will be used which executes a job every minute.

``hour``
  Optional. Execute a :command:`cron` job on a specific hour. If not specified,
  ``*`` will be used which executes a job every hour.

``day``
  Optional. Execute a :command:`cron` job on a specific day of the month. If
  not specified, ``*`` will be used which executes a job every day of the
  month.

``weekday``
  Optional. Execute a :command:`cron` job ona specific day of the week. If not
  specified, ``*`` will be used which executes a job every day of the week.

``special_time``
  Optional. Specify the job execution time using one of the built-in
  :command:`cron` aliases:

  - ``reboot``: execute a job at system boot
  - ``yearly`` or ``annually``: execute a job once a year, at midnight of
    January 1st
  - ``monthly``: execute a job once a month, at midnight of the first day of
    the month
  - ``weekly``: execute a job once a week, at midnight each Sunday
  - ``daily`` or ``midnight``: execute a job once a day, at midnight
  - ``hourly``: execute a job once an hour, on the hour

  Alternatively, you can specify a custom execution time as a string using this
  parameter, for example every March 23rd if it's a Sunday. See the
  :man:`crontab(5)` manual page for details.

``user``
  Optional. Specify the UNIX account which should be used to execute a given
  :command:`cron` job. If not specified, ``root`` will be used by default.


.. _cron__ref_jobs:

cron__jobs
----------

The ``cron__*_jobs`` variables can be used to define what :program:`cron` jobs
should be present on the remote hosts.

The variables are YAML dictionaries or YAML lists (the data type can't be mixed
in the same variable). YAML dictionary keys define the name of the
:program:`cron` configuration file in :file:`/etc/cron.d/` directory.

Each entry is a YAML dictionary that defines a set of one or more
:program:`cron` jobs using specific parameters:

``file`` or ``cron_file``
  Name of the configuration file in the :file:`/etc/cron.d/` directory. Required
  when the YAML list format is used. If not specified, the dictionary key will
  be used as the name.
  Notice in order for a :program:`cron` job to actually be executed, the file
  name must be entirely made up of letters, digits and can only contain the
  special signs underscore ('_') and hyphen ('-').

``environment``
  Optional. A YAML dictionary which defines what variables should be present in
  a given :program:`cron` job environment. Each dictionary key is the variable
  name, and its value will be set as that variable value.

``backup``
  Optional, boolean. If ``True``, the :program:`cron` Ansible module will create
  a backup of an existing configuration file before modifying it.

``job``
  A string that specifies the command that should be executed by
  :program:`cron` to perform a given task.

``jobs``
  List of :program:`cron` jobs which should be defined on the remote host. Each
  list entry is either a string which specifies the command, or a YAML
  dictionary with more specific parameters. Missing parameters that are
  required to define a complete entry will be copied from the main YAML
  dictionary of a given ``cron__*_jobs`` entry.

``custom_files``
  Optional. List of custom files which should be present on the remote host;
  this list can be used to install bigger scripts executed by :program:`cron`
  jobs. Each list entry is a YAML dictionary with specific parameters.
  See below for the description of the parameters.

The parameters below can be specified both in main YAML dictionary, as well as
in a dictionary entry on the ``jobs`` list:

``disabled``
  Optional, boolean. If ``True``, the :program:`cron` entry in the
  configuration file will be commented out, rendering it disabled.

``state``
  Optional. If not specified or ``present``, the :program:`cron` entry will be
  created. If ``absent``, the :program:`cron` entry will be removed. If
  ``ignore``, the existing entries won't be changed and missing entries will
  not be created. If the ``state`` parameter is defined in the main YAML
  dictionary, when it's ``absent`` the entire configuration file will be
  removed.

``user``
  Optional. Specify the UNIX user account which will execute the job. If not
  specified, the job will be executed as the ``root`` account.

``name``
  Optional. Description of a given :program:`cron` job, used as a marker by
  Ansible to correctly manipulate the :program:`cron` entries. if not
  specified, it will be generated automatically to ensure that the
  :program:`cron` jobs are idempotent.

The next set of parameters define when a given :program:`cron` job should be
executed, in the :program:`cron` Ansible module specification format. See its
documentation for more details:

``special_time``
  Specify the special time when the job should be run, in the :program:`cron` format:
  ``hourly``, ``daily``, ``weekly``, ``monthly``, ``annually``, ``yearly``, or
  at the ``reboot``. This parameter cannot be used with other parameters that
  define the execution time.

``minute``
  Specify the minute when the job should be run, in the :program:`cron` format.

``hour``
  Specify the hour when the job should be run, in the :program:`cron` format.

``day``
  Specify the day when the job should be run, in the :program:`cron` format.

``month``
  Specify the month when the job should be run, in the :program:`cron` format.

``weekday``
  Specify what weekdays the job should be run, in the :program:`cron` format.

The parameters below are used in the ``custom_files`` list as the dictionary
keys:

``dest``
  Required. Absolute path to the destination file on the remote host.

``src``
  Absolute path of the source file on the Ansible Controller which will be
  copied to the remote host. Shouldn't be used with the ``content`` parameter.

``content``
  The contents of the specified destination file generated on the remote host.
  Shouldn't be used with the ``src`` parameter.

``owner``
  Optional. Specify the UNIX account of the file owner. If not specified,
  ``root`` will own the file.

``group``
  Optional. Specify the UNIX group the file belongs to. If not specified, it
  will belong to the ``root`` group.

``mode``
  Optional. Specify the file permissions in octal. If not specified, they will
  be set as ``0755``.

``force``
  Optional, boolean. If not specified or ``True``, the role will overwrite any
  existing files. If ``False``, an existing file won't be changed.

Examples
~~~~~~~~

Create two tasks that execute a command every minute, in separate configuration
files.

.. code-block:: yaml

   cron__jobs:

     'simple_job_1':
       job: 'touch /tmp/file1'

     'simple_job_2':
       job: 'touch /tmp/file2'

Create two tasks that execute a command every minute, in separate configuration
files, as a list:

.. code-block:: yaml

   cron__jobs:

     - file: 'simple_job_1'
       job: 'touch /tmp/file1'

     - file: 'simple_job_2'
       job: 'touch /tmp/file2'

Create two tasks that execute a command every minute, in one configuration file:

.. code-block:: yaml

   cron__jobs:
     'two_tasks':
       jobs:

         - 'touch /tmp/file1'

         - 'touch /tmp/file2'

Create a task that executes a command every minute, in the crontab of the user
``jessie``:

.. code-block:: yaml

   cron__jobs:
     'user_cron':
       cron_file: '{{ omit }}'
       user: 'jessie'
       jobs:

         - 'touch /tmp/file1'

Create two tasks in the same file with custom descriptions:

.. code-block:: yaml

   cron__jobs:
     'two_tasks_one_disabled':
       jobs:

         - name: 'This task is done first'
           job: 'touch /tmp/file1'

         - name: 'This task is disabled'
           job: 'touch /tmp/file2'
           disabled: True

Execute a custom script every week, as the ``backup`` user:

.. code-block:: yaml

   cron__jobs:

     'execute-script':
       user: 'backup'
       special_time: 'weekly'
       job: '/usr/local/lib/weekly-job'

       custom_files:

         - dest: '/usr/local/lib/weekly-job'
           content: |
             #!/bin/bash
             touch /tmp/weekly-result
