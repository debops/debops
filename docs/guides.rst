Guides and examples
===================

``debops.postfix`` is designed to manage a Postfix service by itself. Other
Ansible roles can use it as a dependency and influence the Postfix
configuration using dependency variables, but to avoid possible issues they
should not modify Postfix configuration directly. Any changes to Postfix
configuration files not done by ``debops.postfix`` will be overwritten.

