Introduction
============

.. include:: includes/all.rst

Firejail_ is a SUID program that reduces the risk of security breaches by
restricting the running environment of untrusted applications using Linux
namespaces and seccomp-bpf.

This Ansible role allows you to setup and configure Firejail.

Features
~~~~~~~~

* Install Firejail from jessie-backports_ or other configured APT_
  repositories. debops.apt_ can be used to enable Backports if needed.
* Sandbox programs system wide by placing a symlink to :command:`firejail` into the
  ``PATH`` so that :command:`firejail` can wrap program invocations and sandbox the
  invoked program using security profiles that Firejail ships or that the system
  administrator defines.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.3``. To install it, run::

    ansible-galaxy install debops-contrib.firejail

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
