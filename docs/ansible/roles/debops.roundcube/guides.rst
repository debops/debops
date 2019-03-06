Guides and examples
===================

Enable spell checking with aspell
---------------------------------

To enable local spell checking of your email content, you have to install
``php5-enchant`` and ``aspell`` together with the according language
dictionaries. For example for english and french spell checking, you would
add the following packages to your Roundcube role configuration:

.. code:: yaml

   roundcube__packages: [ 'php5-enchant', 'aspell', 'aspell-en', 'aspell-fr' ]

Additionally you have to tell Roundcube that you want to use the local
spell checking library:

.. code:: yaml

   roundcube__local_config_map:
     spellcheck_engine: 'enchant'
     spellcheck_languages: "array('en', 'fr')"

Of course, many more languages are supported. You can find more information
about the required packages and configuration in the Roundcube `defaults.inc.php`_.

.. _defaults.inc.php: https://github.com/roundcube/roundcubemail/blob/master/config/defaults.inc.php
