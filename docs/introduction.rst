Introduction
============

`RStudio`_ is an Integrated Development Environment for R programming language.

This Ansible role will let you deploy RStudio Server, which is RStudio
implemented as a web application accessible in a browser. Basic R environment
will be installed as well (you can also disable RStudio if you want and set up
only R).

Before using this role, you need to provide ``rstudio-server`` and
``libssl0.9.8`` packages for your host using an APT repository. See the Getting
Started guide for more details.

.. _RStudio: http://rstudio.com/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
