postfix_capabilities
~~~~~~~~~~~~~~~~~~~~

List of active Postfix capabilities. By default Postfix is configured with
local mail disabled, all mail is sent to local MX server configured in DNS.

List of available Postfix capabilities:

- ``null``: Postfix has no local delivery, all mail is sent to a MX for current
  domain. Configuration similar to that presented here:
  http://www.postfix.org/STANDARD_CONFIGURATION_README.html#null_client
  Default. You should remove this capability and replace it with others
  presented below.

- ``local``: local delivery is enabled on current host.

- ``network``: enables access to Postfix-related ports (``25``, ``587``,
  ``465``) in firewall, required for incoming mail to be acceped by
  Postfix.

- ``mx``: enables support for incoming mail on port ``25``, designed for hosts set up
  as MX. Automatically enables ``postscreen`` (without ``dnsbl``/``dnswl`` support),
  anti-spam restrictions.

- ``submission``: enables authorized mail submission on ports ``25`` and
  ``587`` (user authentication is currently not supported and needs to be
  configured separately).

- ``deprecated``: designed to enable obsolete functions of mail system,
  currently enables authorized mail submission on port ``465`` (when
  ``submission`` is also present in the list of capabilities).

- ``client``: enable SASL authentication for SMTP client (for outgoing mail
  messages sent via relayhosts that require user authentication).

- ``sender_dependent``: enable sender dependent SMTP client authentication
  (``client`` capability required)

- ``archive``: BCC all mail (or mail from/to specified domains) passing
  through the SMTP server to an e-mail account on local or remote server.

- ``postscreen``: allows to enable postscreen support on port ``25``
  independently of ``mx`` capability.

- ``dnsbl``: enables support for DNS blacklists in postscreen, automatically
  enables whitelists.

- ``dnswl``: enables support for DNS whitelists in postscreen, without blacklists.

- ``test``: enables "soft_bounce" option and XCLIENT protocol extension for
  localhost (useful in mail system testing).

- ``defer``: planned feature to defer mail delivery.

- ``auth``: planned feature to enable user authentication.

Not all combinations of these capabilities will work correctly together.

