Guides and examples
===================

Enable spell checking with aspell
---------------------------------

To enable local spell checking of your email content, you have to install
``php5-enchant`` and ``aspell`` together with the according language
dictionaries. For example for english and french spell checking, you would
add the following packages to your Roundcube role configuration:

    roundcube_extra_packages: [ 'php5-enchant', 'aspell', 'aspell-en', 'aspell-fr' ]

Additionally you have to tell Roundcube that you want to use the local
spell checking library:

    roundcube_local_config_map:
      spellcheck_engine: 'enchant'
      spellcheck_languages: "array('en', 'fr')"

Of course, many more languages are supported. You can find more information
about the required packages and configuration at the Roundcube `Aspell-Howto`_.

.. _Aspell-Howto: http://trac.roundcube.net/wiki/Howto_Config/Aspell
