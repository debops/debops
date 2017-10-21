Custom services and their default ports
=======================================

In various DebOps roles you can find named ports. They are defined in
:file:`/etc/services` using debops.etc_services_ role which manages them using
Ansible's ``assemble`` module. To avoid collisions between various services we
list here custom ports that are set for applications and services that don't
have specified system ports by default.

You can find a list of ports used throughout the DebOps project by running
command::

    debops-defaults | grep '_port:'

This should output list of all variables that define port numbers in various
roles and are available in role defaults, and thus can be overridden by Ansible
inventory.


+----------------+-----------+----------------+
| Service        | Port      | Default bind   |
+================+===========+================+
| apt-cacher-ng  | 3142      | all interfaces |
+----------------+-----------+----------------+
| elasticsearch  | 9200-9400 | localhost      |
+----------------+-----------+----------------+
| etherpad       | 9000      | localhost      |
+----------------+-----------+----------------+
| redis-server   | 6379      | localhost      |
+----------------+-----------+----------------+
| redis-sentinel | 26379     | localhost      |
+----------------+-----------+----------------+
| rails apps     | 3000      | socket         |
+----------------+-----------+----------------+
| gitlab-ci      | 18083     | localhost      |
+----------------+-----------+----------------+

Standard ports
--------------

Run ``cat /etc/services`` to obtain a list of standard ports.

.. _debops.etc_services: https://github.com/debops/ansible-etc_services/

