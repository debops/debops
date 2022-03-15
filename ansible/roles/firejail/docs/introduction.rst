.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2016-2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Introduction
============

.. include:: includes/all.rst

Firejail_ is a SUID program that reduces the risk of security breaches by
restricting the running environment of untrusted applications using Linux
namespaces and seccomp-bpf.

This Ansible role allows you to setup and configure Firejail.

Features
~~~~~~~~

* Installs Firejail from configured APT_ repositories. debops.apt_ can be used
  to enable Backports if needed.
* Sandboxes programs system-wide by placing a symlink to :command:`firejail`
  into the ``PATH`` so that :command:`firejail` can wrap program invocations
  and sandbox the invoked program using security profiles that Firejail ships
  or that the system administrator defines.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.3``. To install it, run::

    ansible-galaxy install debops-contrib.firejail


Note that this role uses features recently introduced in Jinja2, namely
the `equalto` filter which was released with
`Jinja 2.8 <http://jinja.pocoo.org/docs/dev/changelog/#version-2-8>`_ and thus
requires Jinja 2.8.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
