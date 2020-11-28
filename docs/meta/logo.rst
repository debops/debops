.. Copyright (C) 2020 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _debops_logo:

Logo and Images
===============

.. |logo_small| image:: ../../lib/images/debops-small.png
   :width: 50px
   :align: middle
   :target: https://github.com/debops/debops/tree/master/lib/images/debops-small.png

.. |logo| image:: ../../lib/images/debops.png
   :width: 10em
   :align: middle
   :target: https://github.com/debops/debops/tree/master/lib/images/debops.png

.. |logo_text| image:: ../../lib/images/debops-text.png
   :width: 10em
   :align: middle
   :target: https://github.com/debops/debops/tree/master/lib/images/debops-text.png

.. table::
   :widths: 20 40 40
   :align: right

   +--------------+--------+-------------+
   | Icon         | Logo   | Logo & text |
   +--------------+--------+-------------+
   | |logo_small| | |logo| | |logo_text| |
   +--------------+--------+-------------+

The DebOps logo comes in three variants, produced by two different source files.

* `debops-src.svg`__ contains the fully detailed logo and text
* `debops-small-src.svg`__ is a simplified version used to generate icons

.. __: https://github.com/debops/debops/tree/master/lib/images/src/debops-src.svg
.. __: https://github.com/debops/debops/tree/master/lib/images/src/debops-small-src.svg


Copyright and licensing
-----------------------

The design incorporates the *Debian Open Use Logo* as provided in the
`Debian Logos`__ page.

.. __: https://www.debian.org/logos/

The logo was designed by `Tasos Alvas`__ in 2020.

.. __: https://qwertyuiopia.com

The DebOps Logos are Copyright (c) 2020 DebOps.org and Tasos Alvas, and are
released under the terms of the `GNU General Public License`__, version 3 or
any later version or, at your option, of the `Creative Commons Attribution
Share-Alike 4.0 International License`__.

.. __: https://www.gnu.org/licenses/gpl-3.0.html
.. __: https://creativecommons.org/licenses/by-sa/4.0/


Building the DebOps logo
------------------------

The source files for the logo, as well as the ``Makefile`` that generates the
images used on the project, can be found in :file:`lib/images/`.

Since no other parts of the project use image editing tools, the final images
are committed to the repository to avoid cluttering the build pipeline with
redundant dependencies.

To build the logo yourself, you will need:

* ``inkscape``, version 1.0.1 or newer
* The *Quicksand* font, available from the ``fonts-quicksand`` Debian package
* The ``convert`` utility, available from the ``imagemagick`` Debian package
* The ``svgo`` utility, available through ``npm``

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
