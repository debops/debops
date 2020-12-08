.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later
.. _debops.prometheus_server:

debops.prometheus_server
========================

Prometheus__ is a free software application used for event monitoring and
alerting. It records real-time metrics in a time series database (allowing
for high dimensionality) built using a HTTP pull model, with flexible queries
and real-time alerting. The project is written in Go and licensed under the
Apache 2 License, with source code available on GitHub, and is a graduated
project of the Cloud Native Computing Foundation, along with Kubernetes and Envoy.
Ansible roles ``debops.prometheus_exporter``, ``debops.prometheus_alertmanager``
and ``debops.prometheus_server`` allow you to manage a Prometheus server and / or
access remotely to Prometheus exporters and / or Prometheus Alertmanagers in other
hosts.

``debops.prometheus_server`` role is the "server" part - it installs
``prometheus`` Debian package, and configures access to the server with
``nginx`` basic authentication. After that, you can use :ref:`debops.prometheus_exporter`
role to install and configure Prometheus exporters on other hosts to
collect metrics. Also you can use the :ref:`debops.prometheus_alertmanager`
role to install and configure Prometheus Alertmanager in order to include
logic to silence alerts and also to forward them to email, Slack, or
notification services such as PagerDuty.

``debops.prometheus_server`` by default configures node exporter and Alertmanager
scrape configurations with file-based service discovery mechanism that is used
by the :ref:`debops.prometheus_exporter` and :ref:`debops.prometheus_alertmanager`
roles.

.. __: https://en.wikipedia.org/wiki/Prometheus_(software)

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/prometheus_server/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
