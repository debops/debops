## smstools

This is an Ansible role which configures [smstools](http://smstools3.kekekasvi.com/)
package and sets up a TCP -> SMS and mail -> SMS gateway. This role has been
tested on Debian and should work on Debian-based systems.

Several other roles from [ginas](https://github.com/ginas/ginas/) project are
used to configure various parts of the SMS gateway ('postfix' role is used to
create mail -> SMS gateway, 'etc_services', 'ferm' and 'tcpwrappers' are used
to configure TCP service which can be used by other hosts to send SMS messages
over the network).

### Usage examples

#### Sending a text message from command line

You can send SMS messages from the host connected to the GSM modem, by running
command:

    sudo -u smsd sendsms +00123123123 "Text message"

Your user needs to be in `sms` system group or needs to be able to run
`/usr/local/bin/sendsms` script (for example have admin access).

#### Sending a text message using TCP service

SMS messages can be sent remotely using TCP service (by default configured on
port `9898`). Access to the service is protected using tcpwrappers (via
`xinetd` service) and iptables firewall.

To send a text message using TCP service, connect to port `9898` (by default)
and send string similar to (notice lack of quotation marks):

    TEXT +00123123123 Text message

TCP service should respond with text ending with `250 SMS accepted` (if
formatting was correct), or `500 Command not recognized` (if formatting was
incorrect).

Example telnet session which sends SMS message from a localhost:

    $ telnet localhost sms
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    TEXT +00123123123 Text message
    --
    Text: Text message
    To: +00123123123
    250 SMS accepted
    Connection closed by foreign host.

#### Sending a text message over mail

`smstools` role configures two subdomains in local Postfix instance:

  - `sms.` subdomain is responsible for mail to SMS transport, Postfix takes
    mail messages sent to that subdomain and passes them to `sms` service
    (configured in `/etc/postfix/master.cf` which is a script that parses the
    mail message and sends body of that message to specified recipient using
    `sendsms` script;
  - `gsm.` subdomain is used for aliases which correspond to addresses in the
    `sms.` subdomain or groups of aliases in the same subdomain;

To send a SMS message via mail, send a mail to an address `<+00123123123@sms>`
(on localhost) or `<+00123123123@sms.example.com>` (from elsewhere). You can
also create mail aliases using `smstools` role variables or your configured
alias table in format `<name@gsm>` (from localhost) or `<name@gsm.example.com>`
(from elsewhere) which should correspond to mail addresses outlined previously.
Subject of the mail message will be ignored, and body of the message will be
sent using SMS gateway.

## Warning, this role can generate mail backscatter!

At the moment, SMTP server is configured by `smstools` role to accept mail
messages to subdomains specified above and relay them to `sms` transport which
checks if a sender of mail message can send SMS messages through mail. If it
can't, SMTP server receives a reject message and generates a bounce message to
an original sender of the mail, which can be forged, generating [mail
backscatter](https://en.wikipedia.org/wiki/Backscatter_\(email\)).

Because of that risk, at the moment mail -> SMS gateway should be configured on
a separate host behind a trusted mail relay to avoid receiving messages from
unknown mail senders, and should only process mail messages from hosts included
in `mynetworks` Postfix configuration variable.

To fix backscatter issue, `smstools` role needs to have an [external Postfix
access policy service](http://www.postfix.org/SMTPD_POLICY_README.html) which
will be used by Postfix to check if a specific mail sender can send SMS
messages using the gateway. Steps to determine that:

- check recipient domain of a mail message,
  * if recipient domain is one of the supported subdomains (`sms.` or `gsm.`),
    check mail address or domain of the sender against list of allowed
    senders,
    - if mail sender can send SMS messages, return `PERMIT` (or `DUNNO` if
      other checks should be performed),
    - if mail sender is not found, return `REJECT`,
  * otherwise (mail recipient not in a supported domain), return `DUNNO` to
    allow other checks to perform.

Policy service check should be included in `smtpd_recipient_restrictions` list
to be able to check both recipient and sender addresses.

## Known bugs

- `sendsms` script supports sending SMS messages in UTF-8, but `sms-service`
  and `sms-transport` scripts do not, SMS messages are truncated at first
  UTF-8 character.

