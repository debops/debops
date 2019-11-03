.. _debops_policy__distributed_development_model:

Distributed Development Model
=============================

.. include:: ../../includes/global.rst

The DebOps Project relies on a set of tools to allow distributed development in
a secure and authenticated way.

The :command:`git` repositories with :ref:`signed commits and signed tags
<debops_policy__code_signing_policy>` are used as the primary software
distribution method. This allows for distributed development without a single
point of failure.

The GnuPG software, along with it's Web Of Trust is used for user
authentication and authorization. A special :command:`git` repository,
`debops-keyring`_ contains the OpenPGP keyring with the set of current
Developers, Project Leader and Contributors keys which can be used for code
authentication.  SSH keys derived from these OpenPGP keys allow access to the
Project's assets as needed.
