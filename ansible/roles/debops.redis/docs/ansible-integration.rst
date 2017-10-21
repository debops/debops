Ansible integration
===================


.. contents:: Sections
   :local:

The ``debops.redis`` role contains a Python script which is used to gather
information about local Redis and Sentinel services and provide them to other
roles as Ansible local facts. The script outputs its data as a JSON document,
different data will be available depending on the execution environment.

The facts are accessible in Ansible as ``ansible_local.redis.*`` dictionary
variables.

Unprivileged access
-------------------

If the fact script is executed by an unprivileged user account, the script will
return just a basic set of data containing the status of Redis installation
(installed or not installed, enabled if installed) and the name of the system
group which is required to get the rest of the information.

An example output:

.. code-block:: json

   {
     "auth_group": "redis-auth",
     "enabled": true,
     "installed": true
   }

When a privileged user account accesses the fact script, it will return more
information, depending on that account access to the Redis and Sentinel
configuration files.


Single Redis instance
---------------------

Here's an example fact dictionary which can be expected on a single Redis
master instance:

.. code-block:: json

   {
     "auth_group": "redis-auth",
     "enabled": true,
     "host": "localhost",
     "installed": true,
     "password": "<random-long-password>",
     "port": "6379",
     "version": "2.8.17"
   }

You can see here more information, like the host to which the Ansible role
should connect to access the Redis service, the TCP port number the service listens
on, and the authentication password (long random string). If the ``host``
parameter is a DNS hostname, it usually means that this information was taken
from the Ansible inventory directly and was not changed further.


Redis Sentinel cluster
----------------------

Hosts with installed Redis Sentinel (even the ones where Redis Server is
disabled) provide even more useful information through Ansible facts:

.. code-block:: json

   {
     "auth_group": "redis-auth",
     "enabled": true,
     "host": "192.0.2.12",
     "installed": true,
     "monitor": "example-master",
     "password": "<random-long-password>",
     "port": "6379",
     "version": "2.8.17",
     "sentinel_enabled": true,
     "sentinel_monitor_map": {
       "example-master": {
         "master_host": "192.0.2.12",
         "master_port": "6379",
         "password": "<random-long-password>",
         "sentinels": [
           {
             "host": "192.0.2.12",
             "port": "26379"
           },
           {
             "host": "192.0.2.191",
             "port": "26379"
           }
         ],
         "slaves": [
           {
             "host": "192.0.2.126",
             "port": "6379"
           }
         ]
       }
     },
     "sentinel_monitors": [
       "example-master"
     ],
     "sentinel_notify_dir": "/etc/redis/notify.d",
     "sentinel_trigger_dir": "/etc/redis/trigger.d"
   }

Here you can see all Sentinel monitors that have been found in the Sentinel
configuration file by the fact script. The first monitor found has its
configuration exposed in the default facts like ``host``, ``port``,
``password`` (notice the IP address of the host; this usually means that this
value has been modified by the Sentinel dynamically). You can also see the
paths to the ``notify.d`` and ``trigger.d`` directories where other roles can
install hook scripts to be executed by Redis Sentinel on various events.
