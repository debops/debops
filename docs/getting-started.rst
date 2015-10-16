Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::lxc``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``type::dependency``
  This tag specifies which tasks are defined in role dependencies. You can use
  this to omit them using ``--skip-tags`` parameter.

``depend-of::lxc``
  Execute all ``debops.lxc`` role dependencies in its context.

``depend::apt_preferences:lxc``
  Run ``debops.apt_preferences`` dependent role in ``debops.lxc`` context.

``depend::ferm:lxc``
  Run ``debops.ferm`` dependent role in ``debops.lxc`` context.

``depend::ferm:backporter``
  Run ``debops.backporter`` dependent role in ``debops.lxc`` context.
