# Copyright (C) 2026 seven-beep <ebn@entreparentheses.xyz>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only
#
import os
import subprocess


class UnattendedUpgradesPluginNeedRestart:
    """Batch needrestart invocations. Normally needrestart integrates by
    setting up an apt Post-Invoke hook. With minimal steps enabled, this may
    may cause excessive restarts. Instead, skip them all and restart once at
    the end.
    """

    NEEDRESTART_HOOK = "/usr/lib/needrestart/apt-pinvoke"

    def __init__(self):
        self.enabled = True
        self.prerun()

    def prerun(self):
        if "NEEDRESTART_SUSPEND" in os.environ or not os.path.exists(
            self.NEEDRESTART_HOOK
        ):
            self.enabled = False
            return

        # Modify global environment variables inherited to apt and thus
        # needrestart.
        os.environ["NEEDRESTART_SUSPEND"] = "unattended-upgrades"

    def postrun(self, result):
        if not self.enabled:
            return

        del os.environ["NEEDRESTART_SUSPEND"]

        if not result.packages_upgraded:
            return

        subprocess.call([self.NEEDRESTART_HOOK])
