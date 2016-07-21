.. _debops_policy__code_signing_policy:

DebOps code signing policy
==========================

.. include:: includes/all.rst

:Date drafted: 2016-06-19
:Date effective: 2016-09-01
:Last changed: 2016-07-21
:Version: 0.1.0
:Authors: - drybjed_
          - ypid_

.. This version may not correspond directly to the debops-policy version.

The configuration management code and other source code used by the DebOps
Project and committed to its repositories [#debops-org]_ MUST be signed by a
valid PGP key of a DebOps Developer. For contributors it is RECOMMENDED to do
the same.

Patches from DebOps Contributors MUST be reviewed by one of the
DebOps Developers and the merge commit MUST by signed by the DebOps Developer
for this patch to enter the DebOps Project. This should ensure that the last
commit of every repository of the DebOps Project has a valid signature by a
DebOps Developer.

To proof that DebOps Developers and DebOps Contributors have full control over
their account on the source code management platform used to work on the DebOps
Project (currently GitHub) it RECOMMENDED to provide a proof via the means of
https://keybase.io/.

Additionally, it is RECOMMENDED to take part in the Web Of Trust to make
it harder for an adversary to fake signatures by pretending to be one of the
DebOps Contributors or Developers. In particular as the DebOps Project is related to the Debian
Project it is RECOMMENDED to get your key signed by Debian Developers.
A signature from another DebOps Developer is sufficient as well.

This should allow for secure code authentication. That means that tampering
with the code on the source code management platform can be reliable detected
by DebOps tools, DebOps Developers and all of the users of the Project and thus
the integrity of the Project does not rely on centralized parties anymore.
Additionally, this ensures a trusted audit trail.

For background about this refer to:

* `A Git Horror Story: Repository Integrity With Signed Commits <https://mikegerwitz.com/papers/git-horror-story.html>`_
* `What are the advantages and disadvantages of cryptographically signing commits and tags in Git? <https://programmers.stackexchange.com/a/212216>`_
* `Discussion between drybjed and ypid <https://github.com/debops/ansible-ifupdown/pull/48>`_
* `PR of the initial code signing policy <https://github.com/debops/debops-policy/pull/2>`_

.. [#debops-org] All repositories in the DebOps core project currently hosted at: https://github.com/debops/.
   This does not apply for `DebOps Contrib`_.

Policy enforcement schedule
---------------------------

+---------+--------------------+
| Version | Takes effect after |
+=========+====================+
| 0.1.0   | 2016-09-01         |
+---------+--------------------+
| 0.2.0   | 2018-09-01         |
+---------+--------------------+

Planed changes for v0.2.0
-------------------------

* DebOps Contributors MUST sign their work.
