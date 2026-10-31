#!/usr/bin/env python3
import getpass
import sys
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QTabWidget, QWidget,
        QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout,
    )
    from PyQt6.QtGui import QIcon
except ImportError:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QTabWidget, QWidget,
        QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout,
    )
    from PySide6.QtGui import QIcon

FLAG_FILE = Path.home() / ".config" / "ludora" / "welcome-shown"

_CODE = (
    "background:#1e1e2e; color:#cdd6f4; "
    "padding:10px; border-radius:6px; "
    "font-family:monospace; font-size:13px;"
)

WELCOME_HTML = """
<h2>Welcome to Ludora</h2>
<p>You're up and running. Here are a few things worth doing after a fresh install.</p>

<h3>1. Update your system</h3>
<p>Before anything else, run a full system update. See the <b>Upgrading</b> tab for instructions.</p>

<h3>2. Install NVIDIA drivers</h3>
<p>If you have an NVIDIA GPU, see the <b>NVIDIA Drivers</b> tab for step-by-step instructions.</p>

<h3>3. Set up GE-Proton in Steam</h3>
<p>If you installed Steam, GE-Proton is already included. To set it as the default compatibility tool,
open Steam and go to <b>Settings &rarr; Compatibility &rarr; Default compatibility tool</b> and select GE-Proton.</p>

<h3>4. Secure Boot (optional)</h3>
<p>If you want to turn on Secure Boot later, see the <b>Secure Boot</b> tab first &mdash;
turning it on without the setup step stops Ludora from starting.</p>

<p>You can reopen this window any time from <b>System &rarr; Ludora Welcome</b>
in the application menu.</p>
"""

UPGRADE_HTML = f"""
<h2>Keeping Your System Updated</h2>

<p>Do this first after a fresh install, and regularly after that.
Ludora uses <b>dnf</b> for system updates — always use it in a terminal rather than KDE Discover.</p>

<h3>Update your system</h3>
<p>Run this to update all installed packages:</p>
<pre style="{_CODE}">sudo dnf upgrade</pre>
<p>Snapper automatically snapshots your system before each upgrade,
so you can roll back if anything goes wrong.</p>

<h3>Why not KDE Discover?</h3>
<p>KDE Discover is useful for browsing and installing apps, but for full system
upgrades on an RPM-based distro it can be unreliable — sometimes leaving packages
in a broken state or failing without clear output. dnf gives you full control
and readable feedback.</p>
"""

NVIDIA_HTML = f"""
<h2>Installing NVIDIA Drivers</h2>

<p>RPM Fusion NVIDIA repositories are already enabled on your system.
Follow these steps to install the right driver for your GPU.</p>

<h3>Step 1 &mdash; Identify your GPU</h3>
<pre style="{_CODE}">lspci | grep -i nvidia</pre>
<p>Note the model name in the output
(e.g. <i>RTX 4070</i>, <i>GTX 1080 Ti</i>, <i>GTX 680</i>).</p>

<h3>Step 2 &mdash; Choose the right driver</h3>
<table width="100%" cellspacing="0" cellpadding="8"
       style="border-collapse:collapse; margin:6px 0;">
  <tr style="background:#313244; color:#cdd6f4;">
    <th align="left">GPU generation</th>
    <th align="left">Package to install</th>
  </tr>
  <tr style="background:#1e1e2e; color:#cdd6f4;">
    <td>RTX 20xx and newer (Turing+)<br>
        <small>RTX 20xx / 30xx / 40xx / 50xx</small></td>
    <td><code>akmod-nvidia</code></td>
  </tr>
  <tr style="background:#313244; color:#cdd6f4;">
    <td>GTX 750 Ti &mdash; GTX 16xx (Maxwell &amp; Pascal)<br>
        <small>GTX 9xx / 10xx / 16xx</small></td>
    <td><code>akmod-nvidia-580xx</code></td>
  </tr>
  <tr style="background:#1e1e2e; color:#cdd6f4;">
    <td>GTX 600 / GTX 700 series (Kepler)</td>
    <td><code>akmod-nvidia-470xx</code></td>
  </tr>
</table>

<h3>Step 3 &mdash; Install</h3>
<p>The commands below include <code>kernel-ludora-devel-matched</code>, which installs the
kernel headers matching the Ludora kernel. Without it the NVIDIA module cannot be
built and you will boot to a black screen.</p>
<p><b>RTX 20xx and newer:</b></p>
<pre style="{_CODE}">sudo dnf install kernel-ludora-devel-matched akmod-nvidia xorg-x11-drv-nvidia-cuda</pre>
<p><b>GTX 750 Ti &mdash; GTX 16xx (Maxwell &amp; Pascal):</b></p>
<pre style="{_CODE}">sudo dnf install kernel-ludora-devel-matched akmod-nvidia-580xx xorg-x11-drv-nvidia-580xx-cuda</pre>
<p><b>GTX 600 / 700 series (Kepler):</b></p>
<pre style="{_CODE}">sudo dnf install kernel-ludora-devel-matched akmod-nvidia-470xx</pre>

<h3>Step 4 &mdash; Reboot and wait</h3>
<p>After rebooting, the kernel module builds in the background.
This takes about <b>3&ndash;5 minutes</b> on first boot &mdash; do not shut down during this time.
Once built, NVIDIA acceleration is active and survives future kernel updates automatically.</p>

<p><b>Black screen after installing?</b> If you installed the driver without the kernel headers,
switch to a text console (<b>Ctrl+Alt+F3</b>), log in and run:</p>
<pre style="{_CODE}">sudo dnf install kernel-ludora-devel-matched
sudo akmods --force
sudo reboot</pre>

<p><small>Troubleshooting: see the
<a href="https://rpmfusion.org/Howto/NVIDIA">RPM Fusion NVIDIA Howto</a>.</small></p>
"""

SECUREBOOT_HTML = f"""
<h2>Turning On Secure Boot</h2>

<p>Ludora's gaming kernel is not signed by Microsoft, so with Secure Boot on your PC
refuses to start it &mdash; unless you give your PC a signing key of its own first.
If you installed Ludora with Secure Boot already on, this was done during installation
and there is nothing to do here.</p>

<p><b>Do these steps before you turn Secure Boot on in your firmware.</b></p>

<h3>Step 1 &mdash; Create and sign with your key</h3>
<pre style="{_CODE}">sudo dnf install ludora-secureboot
sudo ludora-secureboot setup</pre>
<p>The first line is only needed on installs made before Ludora 45 (it does nothing
if the package is already there). The second creates a key for this PC, signs your kernels with it (new kernels are signed
automatically from now on) and asks you to choose a <b>one-time password</b>.
You only need that password once, in Step 2.</p>

<h3>Step 2 &mdash; Reboot and approve the key</h3>
<p>Reboot. A <b>blue screen</b> appears:</p>
<ol>
  <li>When it says <i>Press any key to perform MOK management</i>, press a key
      <b>within 10 seconds</b>.</li>
  <li>Choose <b>Enroll MOK</b>.</li>
  <li>Choose <b>Continue</b>.</li>
  <li>Choose <b>Yes</b>.</li>
  <li>Type the password you chose in Step 1 and press Enter.
      Nothing is shown while you type. The blue screen uses a US keyboard layout.</li>
  <li>Choose <b>Reboot</b>.</li>
</ol>
<p>Missed the 10 seconds? Run <code>sudo ludora-secureboot setup</code> again and reboot.</p>

<h3>Step 3 &mdash; Check</h3>
<pre style="{_CODE}">sudo ludora-secureboot status</pre>
<p>It should say <b>MOK: enrolled</b> and list every kernel as <b>ok</b>.</p>

<h3>Step 4 &mdash; Turn on Secure Boot</h3>
<p>Now enable Secure Boot in your firmware (BIOS/UEFI) settings.
Do <b>not</b> touch the firmware's key management (clear keys, custom keys, setup mode).</p>
<p>If Ludora does not start afterwards, turn Secure Boot off again, start Ludora and check
<code>sudo ludora-secureboot status</code>.</p>
"""


class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Ludora")
        self.setWindowIcon(QIcon.fromTheme("ludora-start-here"))
        self.setMinimumSize(800, 680)
        self.resize(820, 720)

        tabs = QTabWidget()
        tabs.addTab(self._tab(WELCOME_HTML), "Welcome")
        tabs.addTab(self._tab(UPGRADE_HTML), "Upgrading")
        tabs.addTab(self._tab(NVIDIA_HTML), "NVIDIA Drivers")
        tabs.addTab(self._tab(SECUREBOOT_HTML), "Secure Boot")

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(tabs)
        layout.addLayout(btn_row)
        self.setCentralWidget(central)

    def _tab(self, html):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(html)
        layout.addWidget(browser)
        return w


def main():
    if getpass.getuser() == 'liveuser':
        sys.exit(0)

    force = "--force" in sys.argv

    if not force and FLAG_FILE.exists():
        sys.exit(0)

    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAG_FILE.touch()

    app = QApplication(sys.argv)
    app.setApplicationName("Ludora Welcome")

    win = WelcomeWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
