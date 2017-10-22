.. _kernel_module__ref_default_variable_details:

Default variable details
========================

Some of ``debops-contrib.kernel_module`` variables have more extensive configuration.
Here you can find documentation and examples for them.

.. _kernel_module__ref_kernel_module_list:

kernel_module__list
-------------------

:envvar:`kernel_module__list` and similar lists consist of dictionaries with the
following supported keys:

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
  Defaults to the value of :envvar:`kernel_module__params_force` which defaults to
  ``False``.

Examples
~~~~~~~~

.. code-block:: console

   kernel_module__list:

       ## Ensure that ``nf_conntrack_snmp`` is loaded and automatically during each boot.
     - name: 'nf_conntrack_snmp'

       ## Ensure that ``pcspkr`` is blacklisted.
     - name: 'pcspkr'
       blacklist: yes

       ## Ensure that ``aacraid`` is loaded with the kernel module parameter
       ## ``expose_physicals=1``.
     - name: 'aacraid'
       params: 'expose_physicals=1'
       params_force: True
