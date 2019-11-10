.. _debops_policy__security_policy:

DebOps Security Policy
======================

.. include:: ../../includes/global.rst

.. Based on: https://www.openssl.org/docs/faq.html#BUILD19
   Based on: http://rubyonrails.org/security/
             A: Only legacy HTTP?
   See also: https://security.stackexchange.com/q/34871

   Big parts of the policy have been copied from http://rubyonrails.org/security/.
   Thus, this file is licensed under MIT.

:Date drafted: 2016-07-10
:Date effective:  2016-07-10
:Last changed: 2016-07-10
:Version: 0.1.0
:Authors: - ypid_

.. This version may not correspond directly to the debops-policy version.

Reporting a vulnerability
-------------------------

If you think your bug has security implications then please send it to the
`Current DebOps project Leader`_ and additionally to
the maintainers of the affected part of the project.
If you can fix the vulnerability (or have already done so) please consider
attaching a patch.
Please consider using OpenPGP to encrypt reports before sending them.
You can find the public keys of the team members in the debops-keyring_.

Disclosure process
------------------

#. Security report received and is assigned a primary handler. This person will
   coordinate the fix and release process. Problem is confirmed and a list of
   all affected versions is determined. Code is audited to find any potential
   similar problems.

#. Fixes are prepared for all releases which are still supported. These fixes
   are not committed to the public repository but rather held locally pending
   the announcement.
#. A suggested embargo date for this vulnerability is chosen and potential
   downstream projects of DebOps are notified. This notification will include
   patches for all versions still under support and a contact address for
   packagers who need advice backporting patches to older versions.
#. On the embargo date, the debops-security list is sent a copy of the
   announcement. The changes are pushed to the public repository and affected
   parts of the project are released. Additionally, an GitHub issue is opened
   against the affected repository on GitHub with the intend to inform people
   watching the repository.

This process can take some time, especially when coordination is required with
maintainers of other projects. Every effort will be made to handle the bug in
as timely a manner as possible, however it’s important that we follow the
release process above to ensure that the disclosure is handled in a consistent
manner.

Receiving disclosures
---------------------

The best way to receive all the security announcements is to subscribe to the
`DebOps Security Announcements mailing list`_. The mailing list
is very low traffic, and it receives the public notifications the moment the
embargo is lifted. If you produce packages of DebOps and require prior
notification of vulnerabilities, you should get in touch with the `DebOps project Leader`_.

No one outside the core team, the initial reporter or downstream projects will be
notified prior to the lifting of the embargo. We regret that we cannot make
exceptions to this policy for high traffic or important sites, as any
disclosure beyond the minimum required to coordinate a fix could cause an early
leak of the vulnerability.

If you have any suggestions to improve this policy, please get in touch for
example via
the `debops-policy repository on GitHub <https://github.com/debops/debops-policy>`_.
