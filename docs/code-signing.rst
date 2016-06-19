Code signing policy
===================

The configuration management code and other source code used by the DebOps
Project and committed to its repositories [#debops-org]_ must be signed by a
valid PGP key of a DebOps Developer. This does not yet apply to contributors
(but is highly encouraged).

Patches from DebOps Contributors must be reviewed by one of the
DebOps Developers and the merge commit must by signed by the DebOps Developer
for this patch to enter the DebOps Project. This should ensure that the last
commit of every repository of the DebOps Project has a valid signature by a
DebOps Developer.

To proof that DebOps Developers and DebOps Contributors have full control over
their account on the source code management platform used to work on the DebOps
Project (currently GitHub) it is expected to provide a proof via the means of
https://keybase.io/.

Additionally, it is recommended to take part in the Web of Trust to make
it harder for an adversary to fake signatures by pretending to be one of the
DebOps Developers. In particular as the DebOps Project is related to the Debian
project it is recommended to get your key signed by Debian Developers.

This should allow for secure code authentication. That means that tampering
with the code on the source code management platform can be reliable detected
by DebOps tools, DebOps Developers and all of the users of the project and thus
the integrity of the project does not rely on centralized parties anymore.
Additionally, this ensures a trusted audit trail.

This rule takes effect for DebOps Developer on **1st September 2016**.

DebOps Contributors are expected to sign their work after **1st September 2018**. Before this date, it is highly encouraged.

For background about this refer to:

* `A Git Horror Story: Repository Integrity With Signed Commits <https://mikegerwitz.com/papers/git-horror-story.html>`_
* `What are the advantages and disadvantages of cryptographically signing commits and tags in Git? <https://programmers.stackexchange.com/a/212216>`_
* `Discussion between drybjed and ypid <https://github.com/debops/ansible-ifupdown/pull/48>`_

.. [#debops-org] All repositories in the DebOps core project currently hosted at: https://github.com/debops/.
   This does not apply for `DebOps Contrib <https://github.com/debops-contrib/>`_.
