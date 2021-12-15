.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`rspamd` daemon, maintained by the `Rspamd Project`__, is a
modern spam filtering daemon which can be integrated with any MTA which
supports ``milters``. It provides an advanced spam filtering system that
allows evaluation of messages by a number of rules including regular
expressions, statistical analysis and custom services such as URL black
lists. A web-based user interface is also provided.

.. __: https://rspamd.com/

The ``debops.rspamd`` Ansible role can be used to configure the
:command:`rspamd` service on a host and automatically setup the
:ref:`debops.postfix` role to use it for spam filtering.
