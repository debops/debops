.. _postfix__ref_mastercf:

Default variable details: postfix__mastercf
===========================================


The ``postfix__*_mastercf`` variables are used to define the contents of the
:file:`/etc/postfix/master.cf` configuration file. The variables are YAML
lists, concatenated together into :envvar:`postfix__combined_mastercf`
variable, which is passed to the configuration template.

Each list entry is a YAML dictionary. Entries that control Postfix parameters
of the same name will be combined together in order of appearance.

.. contents::
   :local:
   :depth: 1


Configuration variable format
-----------------------------

The :file:`master.cf` configuration entries are defined using specific
parameters:

``name``
  The name of the Postfix service to manage. This parameter is used as an
  identifier during the variable parsing. If ``command`` parameter is not
  specified, the service will use its name (or ``service`` parameter, if
  present) as the command to execute.

``service``
  Optional. If specified, the service will use this string as the "name" instead
  of the ``name`` value. This is useful to create examples in the configuration
  file that have the same name as existing configuration options.

``type``
  Required. Specify the service type (``inet``, ``unix``, ``fifo``, ``pass``).

``private``
  Optional, boolean. Specify the service "private" status.

``unpriv``
  Optional, boolean. Specify the service "unprivileged" status.

``chroot``
  Optional, boolean. Specify the service "chroot" status.

``wakeup``
  Optional. Time in seconds after which the Postfix master process will connect
  to the service and send a wake up signal.

``maxproc``
  Optional. Maximum number of processes that can run at the same time for
  a given service.

``command``
  Optional. The Postfix command to execute for a given service. If not
  specified, ``service`` and ``name`` parameters are used in that order of
  appearance.

``args``
  Optional. String or an YAML text block with custom arguments to pass to
  a given service.

``options``
  Optional. YAML list of :file:`main.cf` configuration options to override for
  a given service. The syntax is the same as the ``postfix__*_maincf``
  configuration variables. See :ref:`postfix__ref_maincf` for more details.

``comment``
  Optional. String or a YAML dictionary with additional comments for a given
  service.

``separator``
  Optional, boolean. if ``True``, an empty line will be added above a given
  service, useful for readability.

``state``
  Optional. If not specified or ``present``, the service will be present in the
  finished configuration file.

  If ``absent``, the service will not be included in the configuration file.

  If ``ignore``, the given entry will not be evaluated by the role, and no
  changes will be done to the preceding parameters with the same name. This can
  be used to conditionally activate entries with different configuration.

  If ``hidden``, the service will not be displayed in the configuration file,
  but any comments will be present. This can be used to add free-form comments
  in the Postfix configuration file.

  If ``comment``, the service will be present, but it will be commented out.
  This can be used to add examples in the configuration file.

  If ``append``, the given entry will be evaluated only if an entry with the
  same name already exists. The current state will not be changed.

``weight``
  Optional. A positive or negative number which affects the position of a given
  service in the configuration file. The higher the number, the more a given
  service "weighs" and the lower it will be placed in the finished
  configuration file. Negative numbers make the service "lighter" and it will
  be placed higher.

``copy_id_from``
  Optional. This is an internal role parameter which can be used to change the
  relative position of a given option in the configuration file. If you specify
  a name of an option, it's internal "id" number (used for sorting) will be
  copied to the current option. This can be used to move options around to
  different configuration file sections.


Examples
~~~~~~~~

Define a SMTP Postfix service

.. code-block:: yaml

   postfix__mastercf:

     - name: 'smtp'
       type: 'inet'
       private: False
       chroot: True
       command: 'smtpd'

The result of the above configuration in :file:`/etc/postfix/master.cf`:

.. code-block:: none

   smtp      inet  n       -       y       -       -       smtpd

The parameters in the configuration file will be present in the order they were
first defined in the variables, unless the ``weight`` parameter is added, which
will change the order.
