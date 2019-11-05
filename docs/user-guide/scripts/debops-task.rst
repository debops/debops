.. _cmd_debops-task:

The :command:`debops-task` command
==================================

Wraps :command:`ansible`, it can accept anything :command:`ansible` does.

**Note** After ``debops`` is run once and ``ansible.cfg`` is generated, you can
use the :command:`ansible` command directly.

You could use it to run adhoc tasks against your hosts.

Example commands:

.. code:: shell

    debops-task all -m setup

    debops-task somegroup -m shell -a "touch /tmp/foo && rm -rf /tmp/foo"
