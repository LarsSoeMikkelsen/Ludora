#!/usr/bin/env python3
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
<p>Ludora is a Fedora-based Linux distribution built to be ready to use out of the box.
While it includes a curated set of gaming tools, Ludora is designed for anyone who
wants a polished, practical desktop — not just for gamers.</p>

<h3>Always included</h3>
<ul>
  <li><b>RPM Fusion repositories</b> — pre-enabled for drivers, codecs, and extra apps</li>
  <li><b>Btrfs + Snapper</b> — automatic snapshots taken before every system update</li>
</ul>

<h3>Included based on your installation choices</h3>
<ul>
  <li><b>Custom kernel</b> — tuned for responsiveness and gaming workloads</li>
  <li><b>Gaming stack</b> — Vulkan drivers, GameMode, Gamescope and VkBasalt</li>
  <li><b>Gaming applications</b> — Steam, Discord, ProtonPlus, LACT and GOverlay</li>
</ul>

<p>You can reopen this window any time from <b>System &rarr; Ludora Welcome</b>
in the application menu.</p>
"""

UPGRADE_HTML = f"""
<h2>Keeping Your System Updated</h2>

<p>Ludora is based on Fedora and uses <b>dnf</b> as its package manager.
For system upgrades, always use dnf in a terminal rather than KDE Discover.</p>

<h3>Why not KDE Discover?</h3>
<p>KDE Discover is useful for browsing and installing apps, but for full system
upgrades on an RPM-based distro it can be unreliable — sometimes leaving packages
in a broken state or failing without clear output. dnf gives you full control
and readable feedback.</p>

<h3>Regular updates</h3>
<p>Run this to update all installed packages:</p>
<pre style="{_CODE}">sudo dnf upgrade</pre>
<p>Snapper automatically snapshots your system before each upgrade,
so you can roll back if anything goes wrong.</p>

<h3>Major Fedora version upgrade</h3>
<p>When a new Fedora release is available:</p>
<pre style="{_CODE}">sudo dnf system-upgrade download --releasever=45
sudo dnf system-upgrade reboot</pre>
<p>Replace <b>45</b> with the target release number.</p>
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
<p><b>RTX 20xx and newer:</b></p>
<pre style="{_CODE}">sudo dnf install akmod-nvidia xorg-x11-drv-nvidia-cuda</pre>
<p><b>GTX 750 Ti &mdash; GTX 16xx (Maxwell &amp; Pascal):</b></p>
<pre style="{_CODE}">sudo dnf install akmod-nvidia-580xx xorg-x11-drv-nvidia-580xx-cuda</pre>
<p><b>GTX 600 / 700 series (Kepler):</b></p>
<pre style="{_CODE}">sudo dnf install akmod-nvidia-470xx</pre>

<h3>Step 4 &mdash; Reboot and wait</h3>
<p>After rebooting, the kernel module builds in the background.
This takes about <b>3&ndash;5 minutes</b> on first boot &mdash; do not shut down during this time.
Once built, NVIDIA acceleration is active and survives future kernel updates automatically.</p>

<p><small>Troubleshooting: see the
<a href="https://rpmfusion.org/Howto/NVIDIA">RPM Fusion NVIDIA Howto</a>.</small></p>
"""


class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Ludora")
        self.setWindowIcon(QIcon.fromTheme("ludora-start-here"))
        self.setMinimumSize(720, 520)
        self.resize(740, 560)

        tabs = QTabWidget()
        tabs.addTab(self._tab(WELCOME_HTML), "Welcome")
        tabs.addTab(self._tab(UPGRADE_HTML), "Upgrading")
        tabs.addTab(self._tab(NVIDIA_HTML), "NVIDIA Drivers")

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
