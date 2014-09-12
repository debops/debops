Using the custom scripts
========================

- `Where were they installed to?`_
- `debops-update`_
- `debops-init`_
- `debops-task`_
- `debops`_

Where were they installed to?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you allowed them to be installed on your system path then they will be in
``/usr/local/bin`` and directly accessible.

****

debops-update
^^^^^^^^^^^^^

Updates the playbooks and roles relative to ``$PWD``, if none are found
then it will update them at their default location.

****

debops-init
^^^^^^^^^^^

Creates a project for you at the path you specify. After running this script
you should check out ``ansible/inventory/hosts`` relative to your project path.

::

    debops-init ~/myproject

****

debops-task
^^^^^^^^^^^

Wraps ``ansible``, it can accept anything ``ansible`` does.

You could use it to run adhoc tasks against your hosts.

::

    debops-task all -m setup

    debops-task somegroup -m shell "touch /tmp/foo && rm -rf /tmp/foo"

****

debops
^^^^^^

Wraps ``ansible-playbook`` and since that's the most commonly ran command we
decided it's a good idea to shorten it to ``debops`` instead of ``debops-playbook``.

Any arguments that ``ansible-playbook`` supports can be passed to ``debops``.

You don't need to specify an inventory or playbook. Part of the benefit of
using this tool is that it figures out all of that stuff for you. You can still
chain together multiple playbooks, custom or not.

::

    debops -l mygroup

    debops -t foo
