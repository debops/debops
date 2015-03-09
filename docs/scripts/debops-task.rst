The ``debops-task`` command
===========================

Wraps ``ansible``, it can accept anything ``ansible`` does.

**Note** After ``debops`` is run once and ``ansible.cfg`` is generated, you can
use the ``ansible`` command directly.

You could use it to run adhoc tasks against your hosts.

Example commands::

    debops-task all -m setup

    debops-task somegroup -m shell "touch /tmp/foo && rm -rf /tmp/foo"

