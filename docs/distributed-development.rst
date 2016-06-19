Distributed development model
=============================

The DebOps Project relies on a set of tools to allow distributed development in
a secure and authenticated way.

The ``git`` repositories with branches signed commits and tags are used as the
primary software distribution method. This allows for distributed development
without a single point of failure.

The GnuPG software, along with it's Web Of Trust is used for user
authentication and authorization. A special ``git`` repository,
``debops-keyring`` contains ``gpg`` keyrings with set of current Developers,
Project Leader and Contributors keys which can be used for code authentication.
SSH keys derived from these GPG keys allow access to the Project's assets as
needed.

