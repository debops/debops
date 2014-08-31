## debops.mailman

[![Platforms](http://img.shields.io/badge/platforms-debian%20|%20ubuntu-lightgrey.svg)](#)

Install and configure [Mailman](https://www.gnu.org/software/mailman/),
a mailing list manager. It will be installed behind
[Postfix](http://postfix.org/) server (using `debops.postfix` role) which
will serve as an incoming/outgoing mail server, and
[nginx](http://nginx.org/) server (with help of `debops.nginx` role) will
serve the web interface. You can also use this role to create or remove
mailing lists themselves (other management can be done using the web
interface).

### Installation

To install `debops.mailman` using Ansible Galaxy, run:

    ansible-galaxy install debops.mailman

### Role dependencies

- `debops.secret`
- `debops.postfix`
- `debops.nginx`



### Role variables

List of default variables available in the inventory:

    ---
    
    # ---- General options ----
    
    # Should mailman role manage it's own dependencies?
    mailman_dependencies: True
    
    
    # ---- Language and localization ----
    
    # Responses for Debconf questions, need to be the same format as in Debconf.
    # To see available responses, run 'dpkg-reconfigure mailman'
    mailman_debconf_languages: [ 'en (English)' ]
    mailman_debconf_default_language: 'en (English)'
    
    # Default language used on this Mailman host
    mailman_default_language: 'en'
    
    # List of languages (as two-letter names spearated by spaces) to convert to
    # UTF-8 charset using 'convert-mailman-to-utf8' script. If you have primarily
    # English site, you don't need to mess with that. :-)
    mailman_convert_languages: []
    
    
    # --- Site configuration ----
    
    # List of "virtual domains" recognized by Mailman. The first domain on the list
    # will be a default domain. If this list is empty, Mailman will use ansible_fqdn
    # as it's default domain (requires 'local' capability in postfix).
    mailman_domains: [ 'lists.{{ ansible_domain }}' ]
    
    # Site administrator e-mail address
    mailman_site_admin: 'listmaster@{{ ansible_domain }}'
    
    # Postmaster address, required by 'postfix-to-mailman.py' script
    mailman_site_postmaster: 'postmaster@{{ ansible_domain }}'
    
    # Maximum message size enforced by Mailman by default, in kilobytes. Can be
    # changed for each list independently in the web interface
    mailman_max_message_size: '100'
    
    # Maximum number of recipients in each SMTP session
    mailman_smtp_max_recipients: '500'
    
    # Default mailing list, usually 'mailman'
    mailman_site_list: 'mailman'
    
    
    # ---- Web interface and archives ----
    
    # List of hosts or CIDR networks to allow access to Mailman web interface. If
    # the list is empty, allow access from all hosts/networks
    mailman_allow: []
    
    # Should Mailman offer .mbox file in public list archives?
    mailman_public_mbox: True
    
    
    # ---- Passwords ----
    
    # Length of generated passwords for site administrator and list creator access
    mailman_site_password_length: '40'
    
    # Length of generated passwords for mailing list owner/admin access
    mailman_admin_password_length: '30'
    
    # Length of generated passwords for list members
    mailman_member_password_length: '20'
    
    # Should Mailman generate user-friendly passwords?
    mailman_user_friendly_passwords: 'No'
    
    
    # ---- Spam and backscatter prevention ----
    
    # Should auto-discarded messages from non-members be automatically sent to list
    # moderators/admins? Setting this to No will reduce spammy messages to moderators
    mailman_default_forward_auto_discards: 'No'
    
    # How much of the original message should be included in auto-responses?
    mailman_response_include_level: '0'
    
    # What should be done with mail messages from non-members by default? 3 = Discard
    mailman_default_generic_nonmember_action: '3'
    
    # List of domains allowed as referers
    mailman_referers: '{{ (mailman_domains + [ ansible_fqdn, "*." + ansible_domain ]) }}'
    
    
    # ---- Other options ----
    
    # Additional Mailman options in a text block format
    # You can find more options in /usr/lib/mailman/Mailman/Defaults.py
    mailman_options: False
    
    # List of mailing lists to create or remove
    mailman_lists: []
    
      #- name: 'mailing-list'                       # mailing list name, required
      #  domain: 'example.com'                      # specify different domain than the main one
      #  owner: 'root@{{ ansible_domain }}'         # list owner email address
      #  state: 'present,absent'
      #  language: 'en'                             # default list language
      #  purge: False,True                          # remove list archives when deleting?
    
    
    # ---- Mailman patches ----
    
    # List of patches applied to Mailman source code after installation
    # Patch status is saved in /etc/ansible/facts.d/mailman.fact on remote host
    # Set to False to disable patch application
    mailman_patches:
    
      # Add direct link to moderation page
      # https://github.com/okfn/infra/commit/06b83759238e38d1b239ee1e04d75ae3e46365ae
      - 'add-moderator-link.patch'
    
      # Remove automatic capitalization of list names
      # https://mail.python.org/pipermail/mailman-users/2002-January/016732.html
      - 'remove-upper-list-name.patch'
    
      # Ignore commands from non-members (reduces backscatter, but blocks mail registration)
      # https://mail.python.org/pipermail/mailman-users/2013-June/075270.html
      - 'ignore-commands-from-nonmembers.patch'
    
      # Remove extra aliases that are not needed (reduces backscatter)
      # https://mail.python.org/pipermail/mailman-users/2008-March/060870.html
      - 'prune-alias-list.patch'




### Detailed usage guide

Mailman is a bit tricky to manage idempotently - there are many patches
applied during first install, mailing lists are hard to change once they are
created and there might be issues with upgrading of configuration files
(because of that mailman is not upgraded automatically by default). I suggest
that you prepare your Mailman configuration in development environment, and
apply it in production when it's ready.

Postfix will configure Mailman integration differently depending on it's
enabled capabilities:

- with `local` capability Postfix will pass mail messages to Mailman using
  mail aliases and `virtual_alias_maps`/`virtual_alias_domains`;

- without `local` capability Postfix will pass mail messages to Mailman using
  `postfix-to-mailman.py` script, `relay_recipient_maps`, `relay_recipient_domains`
  and `transport_maps`;


### Authors and license

`debops.mailman` role was written by:

- Maciej Delmanowski - [e-mail](mailto:drybjed@gmail.com) | [Twitter](https://twitter.com/drybjed) | [GitHub](https://github.com/drybjed)


License: [GNU General Public License v3](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))


***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).

