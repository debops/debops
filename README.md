## foodsoft

[![GitHub Tags](https://img.shields.io/github/tag/ypid/ansible-foodsoft.svg)](https://github.com/ypid/ansible-foodsoft)
[![GitHub Stars](https://img.shields.io/github/stars/ypid/ansible-foodsoft.svg)](https://github.com/ypid/ansible-foodsoft)


Setup and configure Foodsoft, a web-based software to manage a non-profit food coop (product catalog, ordering, accounting, job scheduling).

For more details checkout the [README from the Foodsoft project][foodsoft.readme].

The role will setup Foodsoft ready for production.

Used Technologies:

* [nginx](http://nginx.org/)
* [Phusion Passenger](https://www.phusionpassenger.com/)
* [MariaDB](https://mariadb.org/)/[MySQL](https://www.mysql.de/)

This role is based on the following documentation:

* https://github.com/foodcoop-adam/foodsoft/wiki/Deployment-%28Debian%29
* https://github.com/foodcoops/foodsoft/blob/master/doc/SETUP_DEVELOPMENT.md#manual-configuration
* https://github.com/foodcoops/foodsoft/blob/master/Dockerfile

And other bits and pieces.

The default of Foodsoft is to redirect to HTTPS so be sure to setup a certificate for example via [debops.pki].
Also note that this role uses the [DebOps](http://debops.org/) project to setup the
webserver and configure the database. Be sure to check it out! :smile: Thanks to [Maciej Delmanowski](https://github.com/drybjed) for the amazing work.

[debops.pki]: https://galaxy.ansible.com/list#/roles/1588
[foodsoft.readme]: https://github.com/foodcoops/foodsoft


### Role dependencies

- `debops.ruby`- `debops.secret`- `debops.mariadb`- `debops.nginx`

### Role variables

List of default variables available in the inventory:

```YAML
---
# Default variables
# =================

# .. contents:: Sections
#    :local:
#
# -------------------
#   System packages
# -------------------

# .. envvar:: foodsoft_base_packages
#
# List of base packages required by foodsoft.
foodsoft_base_packages:

  ## charlock_holmes
  - 'g++'
  ## https://stackoverflow.com/questions/15553792/error-installing-charlock-holmes-error-installing-gitlab/15556110#15556110
  - 'libicu-dev'

  ## RMagick
  - 'pkg-config'
  - 'libmagickwand-dev'

  ## sqlite3
  - 'libsqlite3-dev'

  ## mysql2
  - 'libmysqlclient-dev'
  - 'libmariadbd-dev'

  ## Install via gem
  # - 'ruby-charlock-holmes'
  # - 'ruby-rmagick'

# --------------------
#   Basic options
# --------------------

# .. envvar:: foodsoft_dependencies
#
# Should the ``ypid.foodsoft`` role manage it's own dependencies (database, web server)?
foodsoft_dependencies: True


# .. envvar:: foodsoft_bundler_exclude_groups
#
# Don’t install the Gems in the listed groups.
foodsoft_bundler_exclude_groups:
  - 'test'

  ## Contains SQLite gem.
  - 'development'


# -------------------
#   Web server
# -------------------

# .. envvar:: foodsoft_nginx_server
#
# nginx server configuration for Foodsoft.
foodsoft_nginx_server:
  by_role: 'ypid.foodsoft'
  enabled: True
  type: 'rails'
  name: '{{ foodsoft_domain }}'
  root: '{{ foodsoft_install_path + "/public" }}'

  access_policy: '{{ foodsoft_nginx_access_policy }}'

  # Phusion Passenger options
  passenger_user: '{{ foodsoft_user }}'
  passenger_group: '{{ foodsoft_group }}'
  passenger_options: '{{ foodsoft_passenger_options }}'


# --------------------
#   Database setup
# --------------------

# .. envvar:: foodsoft_database_name
#
# Name of the database to use for Foodsoft.
foodsoft_database_name: 'foodsoft'


# .. envvar:: foodsoft_database_user
#
# Database user for Foodsoft.
foodsoft_database_user: '{{ foodsoft_user }}'


# .. envvar:: foodsoft_database_user
#
# Database user password for Foodsoft.
foodsoft_database_password: "{{ lookup('password', secret + '/mariadb/' +
                                ansible_local.mariadb.delegate_to +
                                '/credentials/' + foodsoft_database_user +
                                '/password length=48') }}"


# .. envvar:: foodsoft_database_configuration
#
# Database configuration. Written to ``sites/public/config/database.yml``.
foodsoft_database_configuration:
  production: &foodsoft_database_configuration_defaults
    adapter: 'mysql2'
    encoding: 'utf8'
    reconnect: 'false'
    database: '{{ foodsoft_database_name }}'
    pool: '5'
    host: '{{ ansible_local.mariadb.server }}'
    username: '{{ foodsoft_database_user }}'
    password: '{{ foodsoft_database_password }}'
    # socket: '/tmp/mysql.sock'

  development:
    <<: *foodsoft_database_configuration_defaults

  # Warning: The database defined as "test" will be erased and
  # re-generated from your development database when you run "rake".
  # Do not set this db to the same as development or production.
  test:
    adapter: 'mysql2'
    encoding: 'utf8'
    reconnect: 'false'
    database: 'foodsoft_test'
    pool: '5'
    host: '{{ ansible_local.mariadb.server }}'
    username: '{{ foodsoft_database_user }}'
    password: '{{ foodsoft_database_password }}'


# ---------------------------
#   Webserver configuration
# ---------------------------

# .. envvar:: foodsoft_webserver_user
#
# Name of the webserver user account which will be granted read only access to
# the Foodsoft application directory.
foodsoft_webserver_user: '{{ ansible_local.nginx.user
                             if (ansible_local|d() and ansible_local.nginx|d() and
                                 ansible_local.nginx.user|d())
                              else "www-data" }}'


# --------------------
#   Foodsoft sources
# --------------------

# .. envvar:: foodsoft_install_repo
#
# URL of the Foodsoft git repository.
foodsoft_install_repo: 'https://github.com/foodcoops/foodsoft.git'
# foodsoft_install_repo: 'https://github.com/foodcoop-adam/foodsoft.git'


# .. envvar:: foodsoft_install_version
#
# Name of the git tag to install. If "HEAD" is chosen then the current
# development checkout will be deployed.
# foodsoft_install_version: 'HEAD'
foodsoft_install_version: '7801b364c9bce770a1321eb58d5f0486dc67cb24'
## 4.4.1


# --------------------
#   Foodsoft directory layout
# --------------------

# .. envvar:: foodsoft_home
#
# Application installation directory.
foodsoft_home: '{{ (ansible_local.nginx.www
	            if (ansible_local|d() and ansible_local.nginx|d() and
	                ansible_local.nginx.www|d())
	            else "/srv/www") + "/" + foodsoft_user }}'


# .. envvar:: foodsoft_install_path
#
# Path where Foodsoft application source will be installed, this directory
# should be readable by the webserver.
foodsoft_install_path: '{{ foodsoft_home + "/sites/public" }}'


# --------------------
#   Internal application settings ----
# --------------------

# .. envvar:: foodsoft_user
#
# Name of the system user account for Foodsoft.
foodsoft_user: 'foodsoft'

# .. envvar:: foodsoft_user
#
# Name of the system group account for Foodsoft.
foodsoft_group: 'foodsoft'


# .. envvar:: foodsoft_user_append_groups
#
# List of additional system groups to add to the foodsoft user account.
foodsoft_user_append_groups: []


# .. envvar:: foodsoft_user_append_groups
#
foodsoft_domain: [ 'foodsoft.{{ ansible_domain }}' ]


# .. envvar:: foodsoft_nginx_access_policy
#
# Name of webserver access policy to enable. Refer to ``debops.nginx`` for
# details.
foodsoft_nginx_access_policy: ''


# .. envvar:: foodsoft_passenger_options
#
# Additional options for Phusion Passenger as text block
foodsoft_passenger_options: ''
# foodsoft_passenger_options: 'passenger_friendly_error_pages on;'


# .. envvar:: foodsoft_name
#
# Name of this Foodcoop.
foodsoft_name: 'FC Test'


# .. envvar:: foodsoft_contact
#
# Foodcoop contact information (used for FAX messages).
foodsoft_contact:
  street: 'Grüne Straße 103'
  zip_code: '10997'
  city: 'Berlin'
  country: 'Deutschland'
  email: 'foodsoft@foodcoop.test'
  phone: '030 323 23249'


# .. envvar:: foodsoft_homepage
#
# Homepage.
foodsoft_homepage: 'https://{{ foodsoft_domain[0] }}/{{ foodsoft_default_scope }}'


# .. envvar:: foodsoft_custom_url
#
# Custom foodsoft software URL (used in footer).
foodsoft_custom_url: ''


# .. envvar:: foodsoft_email_sender
#
# Email address to be used as sender.
foodsoft_email_sender: 'foodsoft@foodcoop.test'


# .. envvar:: foodsoft_error_recipients
#
# Email address to be used as sender.
foodsoft_error_recipients:
  - 'admin@foodcoop.test'


# .. envvar:: foodsoft_multi_coop_install
#
# If you wanna serve more than one Foodcoop with one installation.
# Don't forget to setup databases for each Foodcoop. See also MULTI_COOP_INSTALL.
foodsoft_multi_coop_install: 'false'


# .. envvar:: foodsoft_multi_coop_install
#
# If ``foodsoft_multi_coop_install`` is true you have to use a coop name, which
# you you wanna be selected by default.
foodsoft_default_scope: 'f'


# .. envvar:: foodsoft_use_nick
#
# When use_nick is enabled, there will be a nickname field in the user form,
# and the option to show a nickname instead of full name to foodcoop members.
# Members of a user's groups and administrators can still see full names.
foodsoft_use_nick: false


# .. envvar:: foodsoft_use_wiki
#
# Most plugins can be enabled/disabled here as well. Messages and wiki are enabled
# by default and need to be set to false to disable. Most other plugins needs to
# be enabled before they do anything.
foodsoft_use_wiki: true


# .. envvar:: foodsoft_use_messages
#
# Most plugins can be enabled/disabled here as well. Messages and wiki are enabled
# by default and need to be set to false to disable. Most other plugins needs to
# be enabled before they do anything.
foodsoft_use_messages: true


# .. envvar:: foodsoft_page_footer
#
# Page footer (html allowed). Default is a Foodsoft footer. Set to the word
# "blank" for no footer. If unchanged, the default footer of Foodsoft will be used.
foodsoft_page_footer: ''


# .. envvar:: foodsoft_price_markup
#
# Price markup in percent.
foodsoft_price_markup: 2.0


# .. envvar:: foodsoft_tax_default
#
# Default vat percentage for new articles.
foodsoft_tax_default: 7.0


# .. envvar:: foodsoft_app_configuration
#
# Foodsoft configuration. Written to ``sites/public/config/app_config.yml``.
foodsoft_app_configuration:
  default: &defaults
    # If you wanna serve more than one foodcoop with one installation
    # Don't forget to setup databases for each foodcoop. See also MULTI_COOP_INSTALL
    multi_coop_install: false

    # If multi_coop_install you have to use a coop name, which you you wanna be selected by default
    default_scope: '{{ foodsoft_default_scope }}'

    # name of this foodcoop
    name: '{{ foodsoft_name }}'
    # foodcoop contact information (used for FAX messages)
    contact: '{{ foodsoft_contact }}'

    # Homepage
    homepage: '{{ foodsoft_homepage }}'

    # foodsoft documentation URL
    help_url: https://github.com/foodcoops/foodsoft/wiki/Doku

    # documentation URL for the apples&pears work system
    applepear_url: https://github.com/foodcoops/foodsoft/wiki/%C3%84pfel-u.-Birnen

    # custom foodsoft software URL (used in footer)
    foodsoft_url: '{{ foodsoft_custom_url }}'
    #foodsoft_url: https://github.com/foodcoops/foodsoft

    # Default language
    #default_locale: en
    # By default, foodsoft takes the language from the webbrowser/operating system.
    # In case you really want foodsoft in a certain language by default, set this to true.
    # When members are logged in, the language from their profile settings is still used.
    #ignore_browser_locale: false
    # Default timezone, e.g. UTC, Amsterdam, Berlin, etc.
    #time_zone: Berlin
    # Currency symbol, and whether to add a whitespace after the unit.
    #currency_unit: €
    #currency_space: true

    # price markup in percent
    price_markup: '{{ foodsoft_price_markup }}'

    # default vat percentage for new articles
    tax_default: '{{ foodsoft_tax_default }}'

    # tolerance order option: If set to false, article tolerance values do not count
    # for total article price as long as the order is not finished.
    tolerance_is_costly: false

    # Ordergroups, which have less than 75 apples should not be allowed to make new orders
    # Comment out this option to activate this restriction
    #stop_ordering_under: 75

    # Comment out to completely hide apple points (be sure to comment stop_ordering_under)
    #use_apple_points: false

    # ordergroups can only order when their balance is higher than or equal to this
    # not fully enforced right now, since the check is only client-side
    #minimum_balance: 0

    # how many days there are between two periodic tasks
    #tasks_period_days: 7
    # how many days upfront periodic tasks are created
    #tasks_upfront_days: 49

    # default order schedule, used to provide initial dates for new orders
    # (recurring dates in ical format; no spaces!)
    #order_schedule:
    #  ends:
    #    recurr: FREQ=WEEKLY;INTERVAL=2;BYDAY=MO
    #    time: '9:00'
    #  # reference point, this is generally the first pickup day; empty is often ok
    #  #initial:

    # When use_nick is enabled, there will be a nickname field in the user form,
    # and the option to show a nickname instead of full name to foodcoop members.
    # Members of a user's groups and administrators can still see full names.
    use_nick: '{{ foodsoft_use_nick }}'

    # Most plugins can be enabled/disabled here as well. Messages and wiki are enabled
    # by default and need to be set to false to disable. Most other plugins needs to
    # be enabled before they do anything.
    use_wiki: '{{ foodsoft_use_wiki }}'
    use_messages: '{{ foodsoft_use_messages }}'

    # Base font size for generated PDF documents
    #pdf_font_size: 12
    # Page size for generated PDF documents
    #pdf_page_size: A4
    # Some documents (like group and article PDFs) can include page breaks
    # after each sublist.
    #pdf_add_page_breaks: true
    # Alternatively, this can be set for each document.
    #pdf_add_page_breaks:
    #  order_by_groups: true
    #  order_by_articles: true


    # Page footer (html allowed). Default is a Foodsoft footer. Set to `blank` for no footer.
    page_footer: '{{ foodsoft_page_footer }}'

    # Custom CSS for the foodcoop
    # custom_css: 'body { background-color: #fcffba; }'

    # Uncomment to add tracking code for web statistics, e.g. for Piwik. (Added to bottom of page)
    #webstats_tracking_code: |
    #  <!-- Piwik -->
    #  ......

    # email address to be used as sender
    email_sender: '{{ foodsoft_email_sender }}'

    # If your foodcoop uses a mailing list instead of internal messaging system
    #mailing_list: list@example.org
    #mailing_list_subscribe: list-subscribe@example.org

    # Config for the exception_notification plugin
    notification:
      error_recipients: '{{ foodsoft_error_recipients }}'
      sender_address: '"Foodsoft Error" <{{ foodsoft_email_sender }}>'
      email_prefix: "[Foodsoft]"

    # http config for this host to generate links in emails (uses environment config when not set)
    #protocol: http
    #host: localhost
    #port: 3000

    # Access to sharedlists, the external article-database.
    # This allows a foodcoop to subscribe to a selection of a supplier's full assortment,
    # and makes it possible to share data with several foodcoops. Using this requires installing
    # an additional application with a separate database.
    #shared_lists:
    #  adapter: mysql2
    #  host: localhost
    #  database: sharedlists_development
    #  username: root
    #  password:
    #  encoding: utf8
    #  socket: /opt/lampp/var/mysql/mysql.sock

  development:
    <<: *defaults

  test:
    <<: *defaults

  production:
    <<: *defaults
```




### Authors and license

`foodsoft` role was written by:

- [Robin Schneider](https://github.com/ypid) | [e-mail](mailto:ypid@riseup.net)

License: [AGPLv3](https://tldrlegal.com/license/gnu-affero-general-public-license-v3-%28agpl-3.0%29)

***

README generated by [Ansigenome](https://github.com/nickjj/ansigenome/).
