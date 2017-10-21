## backup-debops.org.sh

This script can be used to backup essential git repositories of the
[DebOps](https://debops.org/) project.

Current list of git repositories is stored in `backup-data.txt` file (it is
a shell script with the list of repositories stored in arrays, sourced by the main
script). This file is downloaded directly from GitHub, so that the list of the
repositories can be easily updated (new roles are added from time to time, some
roles are removed, etc.) and kept up-to-date without changing the main script.

#### Security

To prevent tampering and code injection by a MITM attack in the part of the
script sourced from the data file, the list of repositories is signed by a GPG key
`0xA1BAC21E8F22D9E4` (author's own key) and signature is provided in a separate
file. Backup script downloads both files to a random temporary directory and
checks the validity of the signature before sourcing the data file. If the
signature is invalid, script exits immediately.

To enable backup, you will need to import the GnuPG key used to sign the
repository list. To do that, on the user account that will manage the backup
(do NOT use the `root` user account), issue the command:

    gpg --recv-keys '955CA868949DF13B6375851898BC72D3E3B451EA'

This will download and import the correct key used to sign the repository list
from your configured keyserver. If you don't have GnuPG configured, you can
read a [best
practices](https://help.riseup.net/en/security/message-security/openpgp/best-practices)
document to find out how to do this.

#### General usage

When the correct key is imported in the GnuPG keyring, you can run the script itself:

    ./backup-debops.org.sh

Script will create `debops.org/` subdirectory in your current directory and
mirror all listed git repositories inside. By default, script will create bare
mirrors of the repositories, without checking out the actual files.

Full script arguments:

    backup-debops.org.sh [directory] [mode]

* `directory` is a directory in your filesystem where backups should be stored;
* `mode` is a mode of operation for the script:
  - `mirror` (default) will mirror all repositories to bare git repositories
  - `backup` will clone all git repositories and check them out immediately
  - `restore` will check out all repositories from local mirror

#### Usage from cron

`backup-debops.org.sh` script can be run by `cron` to easily handle updates.
Already cloned repositories will fetch or pull newest updates from the `origin`
repositories (depending on mode of operation, `mirror` or `backup`). Script
automatically creates and maintains a lockfile to prevent accidental race
conditions when a backup process takes too long.

Example usage from a `cron`, accessed via `crontab -e`:

    0 3 * * * /home/user/backup-debops.org.sh /home/user/backups > /dev/null

Above command will run the backup script at 3AM each day and create backups in
`~/backups/debops.org/` directory on the user's account.

