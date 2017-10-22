Design goals
============

.. include:: includes/all.rst

- Don’t overwrite global configuration files like
  :file:`/etc/initramfs-tools/initramfs.conf` and similar as this can lead to
  problems like newer package versions trying to upgrade the file.
  :file:`/etc/initramfs-tools/conf.d` and other :file:`*.d` directories are
  preferred and used for this.

- If additional kernel modules need to be loaded in the initramfs then this
  functionally should be added to the debops-contrib.kernel_module_ role.
  Note that all modules listed in :file:`/etc/initramfs-tools/modules` are
  force loaded as can be read in :file:`/usr/sbin/mkinitramfs`.
  An initramfs hook should be used instead of touching the
  :file:`/etc/initramfs-tools/modules` file.
