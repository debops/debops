Default variables: configuration
================================

Some of ``ypid.kernel_module`` variables have more extensive configuration.
Here you can find documentation and examples for them.

kernel_module_list
------------------

``name``
  Required, string. Name of the kernel module.

``blacklist``
  If true, blacklist the module. Note that blacklist dominates the loading of
  modules.
  Defaults to ``False``.

``state``
  Optional, string. If ``present`` load the module unless it is blacklisted.
  Use ``absent`` to unload the module.
  Defaults to ``present``.

``persistent``
  Optional, boolean. If ``True``, make changes permanent else the changes will not
  persist a reboot.
  Defaults to ``True``.

``params``
  Optional, string or list of strings. Kernel module parameters.
  Example:

  .. code:: YAML

     - name: 'aacraid'
       params: [ 'expose_physicals=1', 'cache=0' ]

``params_force``
  Optional, boolean. If ``True``, force that the module parameters are applied
  (via unloading and loading of the module).
  Defaults to the value of ``kernel_module_params_force`` which defaults to
  ``False``.
