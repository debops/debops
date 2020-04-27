.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later
.. _debops.prometheus_alertmanager:

debops.prometheus_alertmanager
==============================

Prometheus__ is a free software application used for event monitoring and
alerting. It records real-time metrics in a time series database (allowing
for high dimensionality) built using a HTTP pull model, with flexible queries
and real-time alerting. The project is written in Go and licensed under the
Apache 2 License, with source code available on GitHub, and is a graduated
project of the Cloud Native Computing Foundation, along with Kubernetes and Envoy.
Ansible roles ``debops.prometheus_exporter``, ``debops.prometheus_alertmanager``
and ``debops.prometheus_server`` allow you to manage a Prometheus server and / or
access remotely to Prometheus exporters and / or Prometheus alertmanagers in other
hosts.

``debops.prometheus_alertmanager`` installs ``prometheus-alertmanager`` Debian
package, configures access to the web interface with ``nginx`` basic authentication
and it uses Ansible delegation to configure access from the Prometheus server
using file-based service discovery mechanism. You can use ``debops.prometheus_server``
role to manage the Prometheus server itself.

.. __: https://en.wikipedia.org/wiki/Prometheus_(software)

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/prometheus_alertmanager/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
