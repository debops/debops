.. _prometheus_server__ref_default_variable_details:

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.prometheus_server`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 2


.. _prometheus_server__ref_servers:

prometheus_server__jobs
-----------------------

Common role options
~~~~~~~~~~~~~~~~~~~

``state``
  Optional, string. Defaults to ``present``.
  Whether the prometheus_server server should be ``present`` or ``absent``.

``content``
  Is used directly as scape_config from prometheus.
  https://prometheus.io/docs/prometheus/latest/configuration/configuration/#<scrape_config>


