.. _cran__ref_defaults_detailed:

Default variable details
========================

Some of ``debops.cran`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _cran__ref_r_packages:

cran__r_packages
----------------

The ``cran__*_r_packages`` variables define what R packages will be installed
by Ansible system-wide, in the :file:`/usr/local/lib/R/site-library/`
directory. Each variable contains a list of entries, an entry can be a simple
string with the package name, which will be installed if available.
Alternatively an entry can be a YAML dictionary with specific parameters:

``name``
  Required. Name of the R package to install or remove.

``state``
  Optional. If not specified or ``present``, the specific R package will be
  installed. If ``absent``, the specific R package will be removed.

``repo``
  Optional. URL of the repository with the R packages to use. If not specified,
  the value of the :envvar:`cran__upstream_mirror` variable will be used by
  default.

Examples
~~~~~~~~

Install selected R packages system-wide:

.. code-block:: yaml

   cran__r_packages:

     - 'Rcpp'

     - 'ggplot2'

     - name: 'plyr'
       state: 'present'
