.. _debops_policy__code_signing_policy:

DebOps Code Signing Policy
==========================

.. include:: ../../includes/global.rst

:Date drafted: 2016-06-19
:Date effective: 2016-09-01
:Last changed: 2016-08-07
:Version: 0.1.0
:Authors: - drybjed_
          - ypid_

.. This version may not correspond directly to the debops-policy version.

Terminology
-----------

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14, [`RFC2119`_].

Policy
------

The configuration management code and other source code used by the DebOps
Project and committed to its repositories [#debops-org]_ MUST be signed by a
valid OpenPGP key of a DebOps Developer. For contributors it is RECOMMENDED to do
the same.

Patches from DebOps Contributors MUST be reviewed by one of the
DebOps Developers and the merge commit MUST by signed by the DebOps Developer
for this patch to enter the DebOps Project. This should ensure that the last
commit of every repository of the DebOps Project has a valid signature by a
DebOps Developer.

This should allow for secure code authentication. That means that tampering
with the code on the source code management platform can be reliable detected
by `DebOps Tools`_, DebOps Developers and all of the users of the Project and thus
the integrity of the Project does not rely on centralized parties anymore
(`not yet implemented <https://github.com/debops/debops-tools/issues/164>`__).
Additionally, this ensures a trusted audit trail.

Refer to the debops-keyring_ where a copies of the OpenPGP keys are present
which can be used to verify the signatures.

.. [#debops-org] All repositories in the DebOps core project currently hosted at: https://github.com/debops/.
   This does not apply for `DebOps Contrib`_.

Additional References
---------------------

* `Git Tools - Signing Your Work <https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work>`_
* `A Git Horror Story: Repository Integrity With Signed Commits <https://mikegerwitz.com/papers/git-horror-story.html>`_
* `What are the advantages and disadvantages of cryptographically signing commits and tags in Git? <https://programmers.stackexchange.com/a/212216>`_
* `Discussion between drybjed and ypid <https://github.com/debops/ansible-ifupdown/pull/48>`_
* `PR of the initial code signing policy <https://github.com/debops/debops-policy/pull/2>`_
* `Issue "sign all git commits" started by @adrelanos <https://github.com/micahflee/onionshare/issues/221>`_ (which also includes various pointers)
