Changelog
=========

v0.1.0
------

*Unreleased*

- Change the default ``olcAccess`` rules to not allow users to modify all of
  their own attributes by default. Fixes `Debian Bug #761406`_. [drybjed]

.. _Debian Bug #761406: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=761406

- Move ``olcSecurity`` rules to role defaults, so that they can be easily
  overridden if necessary. [drybjed]

- First release, add CHANGES.rst [drybjed]

