Changelog
=========

v0.1.0
------

*Unreleased*

- Create missing import directory for CSV files. [drybjed]

- Add support for ``phpipam-scripts``, a set of Python/Bash scripts which
  export the data from phpIPAM database as DHCP configuration files. [drybjed]

- Change the phpIPAM repository location. [drybjed]

- Change the ``phpipam`` home directory from ``/nonexistent`` to (by default)
  ``/var/local/phpipam``. Home directory will be created automatically by
  ``sudo``, so it should be distinct. [drybjed]

- Check if ``BASE`` constant in ``config.php`` is defined before defining it
  again, prevents constant notice messages in nginx ``error.log``. [drybjed]

- Add ``php5-gd`` to list of required PHP5 packages for CAPTCHA. [drybjed]

- Update ``nginx`` location block to support "pretty links" mode in phpIPAM,
  fixes issues with URL redirects. [drybjed]

- Add Changelog. [drybjed]

