"""Window for ludora-leave.

Runs as the user. It shows what leaving Ludora will do (ludora-leave
--plan-json, no root needed) and asks for the password only when the user
presses Leave Ludora; then it runs 'pkexec ludora-leave --yes' and shows its
progress.
"""
import html
import json
import re
import sys

from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
                             QMessageBox, QPlainTextEdit, QProgressBar,
                             QPushButton, QStackedWidget, QTextBrowser,
                             QVBoxLayout, QWidget)

EXE = "/usr/bin/ludora-leave"
STEPS = 8
STEP_RE = re.compile(r"^==> (\d)/8 (.*)$")

INTRO = """
<h2>Leave Ludora</h2>
<p>This turns this computer back into plain Fedora KDE, without a reinstall.
Your files, apps, Steam games, Flatpaks and RPM Fusion stay as they are.</p>
<p><b>Nothing is changed until you press <i>Leave Ludora</i>.</b> Only then
does the system ask for your password, in a window that says
<i>Leave Ludora</i>.</p>
"""


def esc(s):
    return html.escape(str(s))


def plan_html(P, mok_password):
    li = []
    li.append("Take a snapshot named <i>Before leaving Ludora</i>.")
    li.append("Remove the Ludora repository." if P["copr"]
              else "The Ludora repository is already removed.")
    li.append("Install Fedora's kernel and make it the one that starts"
              + (", with the files akmods needs to build NVIDIA drivers for it."
                 if P["akmods"] else "."))
    if P["remove"]:
        t = "Remove the packages that only Ludora has:<br><small>" + \
            ", ".join(esc(n) for n in P["remove"]) + "</small>"
    else:
        t = "Ludora-only packages: none left to remove."
    for n, by in P["kept"].items():
        t += f"<br><small>Kept: {esc(n)} (needed by {esc(', '.join(by))})</small>"
    li.append(t)
    if P["swap"]:
        li.append("Replace Ludora's builds of Fedora packages with Fedora's own:"
                  "<br><small>" + ", ".join(esc(n) for n in P["swap"]) + "</small>")
    else:
        li.append("Ludora's builds of Fedora packages: none left to replace.")
    li.append("Bring back Fedora's boot splash, boot menu names and firmware "
              "boot entry, and Discover's offline updates; remove Ludora's "
              "leftover files in home folders.")
    if P["mok"] == "enrolled":
        if P["may_delete_key"]:
            li.append("Delete the Ludora Secure Boot key, if you tick the box below.")
        else:
            li.append("Keep the Ludora Secure Boot key: akmods (for example "
                      "NVIDIA) signs drivers with it.")
    li.append("Remove this tool. Fedora's kernel starts after the reboot.")
    out = "<h3>What will happen</h3><ol>" + \
        "".join(f"<li style='margin-bottom:6px'>{x}</li>" for x in li) + "</ol>"
    out += ("<h3>Afterwards</h3><p>The Ludora desktop look stays until you pick "
            "another one in System Settings &gt; Colors &amp; Themes &gt; Global "
            "Theme (Fedora's default is Breeze). Snapshots taken so far stay.</p>")
    return out


class Window(QWidget):
    def __init__(self, mok_password):
        super().__init__()
        self.mok_password = mok_password
        self.plan = None
        self.proc = None
        self.running = False
        self.setWindowTitle("Leave Ludora")
        self.setWindowIcon(QIcon.fromTheme("system-switch-user"))
        self.resize(720, 640)

        self.stack = QStackedWidget()
        lay = QVBoxLayout(self)
        lay.addWidget(self.stack)

        # page 0: plan
        p0 = QWidget()
        v = QVBoxLayout(p0)
        self.text = QTextBrowser()
        self.text.setOpenExternalLinks(True)
        v.addWidget(self.text)
        self.keybox = QCheckBox(
            "Also delete the Ludora Secure Boot key (Fedora's kernel does not need "
            "it). At the next boot a blue screen asks you to confirm, with the "
            f"password '{mok_password}'. Keeping it is harmless.")
        self.keybox.setVisible(False)
        v.addWidget(self.keybox)
        row = QHBoxLayout()
        row.addStretch()
        self.cancel = QPushButton("Close")
        self.cancel.clicked.connect(self.close)
        self.go = QPushButton("Leave Ludora…")
        self.go.setEnabled(False)
        self.go.clicked.connect(self.confirm)
        row.addWidget(self.cancel)
        row.addWidget(self.go)
        v.addLayout(row)
        self.stack.addWidget(p0)

        # page 1: progress
        p1 = QWidget()
        v = QVBoxLayout(p1)
        self.status = QLabel()
        self.status.setWordWrap(True)
        f = self.status.font()
        f.setPointSizeF(f.pointSizeF() * 1.2)
        self.status.setFont(f)
        v.addWidget(self.status)
        self.bar = QProgressBar()
        self.bar.setRange(0, STEPS)
        v.addWidget(self.bar)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        self.details.setMaximumBlockCount(5000)
        v.addWidget(self.details)
        row = QHBoxLayout()
        row.addStretch()
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        self.reboot_btn = QPushButton("Reboot now")
        self.reboot_btn.clicked.connect(self.reboot)
        row.addWidget(self.close_btn)
        row.addWidget(self.reboot_btn)
        v.addLayout(row)
        self.stack.addWidget(p1)

        self.load_plan()

    # -- plan (as the user) --
    def load_plan(self):
        self.text.setHtml(INTRO + "<p><i>Checking what is installed and what "
                          "Fedora's repositories offer (this can take a minute) "
                          "&hellip;</i></p>")
        self.go.setEnabled(False)
        p = QProcess(self)
        p.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        p.setStandardInputFile(QProcess.nullDevice())
        p.finished.connect(lambda *_: self.plan_done(p))
        p.start(EXE, ["--plan-json"])

    def plan_done(self, p):
        raw = bytes(p.readAllStandardOutput()).decode(errors="replace")
        try:
            P = json.loads(raw.strip().splitlines()[-1])
        except (ValueError, IndexError):
            err = bytes(p.readAllStandardError()).decode(errors="replace")
            P = {"error": "Could not work out the plan.\n" + err[-2000:]}
        if "error" in P:
            self.text.setHtml(INTRO + f"<p><b>{esc(P['error'])}</b></p>")
            return
        if P["nothing"]:
            self.text.setHtml("<h2>Leave Ludora</h2><p>Nothing from Ludora is "
                              "installed or configured here.</p>")
            return
        self.plan = P
        self.text.setHtml(INTRO + plan_html(P, self.mok_password))
        self.keybox.setVisible(P["may_delete_key"])
        self.go.setEnabled(True)

    # -- leave (as root, via pkexec) --
    def confirm(self):
        m = QMessageBox(self)
        m.setIcon(QMessageBox.Icon.Warning)
        m.setWindowTitle("Leave Ludora")
        m.setText("Leave Ludora now?")
        m.setInformativeText(
            "The steps above run now and take a few minutes. Keep the computer "
            "on and connected until it says Done. The system asks for your "
            "password next.")
        yes = m.addButton("Leave Ludora", QMessageBox.ButtonRole.AcceptRole)
        m.addButton(QMessageBox.StandardButton.Cancel)
        m.exec()
        if m.clickedButton() is yes:
            self.start()

    def start(self):
        args = [EXE, "--yes"]
        if self.keybox.isVisible() and self.keybox.isChecked():
            args.append("--delete-key")
        self.stack.setCurrentIndex(1)
        self.status.setText("Waiting for your password …")
        self.bar.setValue(0)
        self.details.clear()
        self.close_btn.setEnabled(False)
        self.reboot_btn.setVisible(False)
        self.running = True
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.proc.setStandardInputFile(QProcess.nullDevice())
        self.proc.readyReadStandardOutput.connect(self.output)
        self.proc.finished.connect(self.done)
        self.proc.start("pkexec", args)

    def output(self):
        data = bytes(self.proc.readAllStandardOutput()).decode(errors="replace")
        if data and self.bar.value() == 0 and not self.status.text().startswith("Step"):
            self.status.setText("Checking Fedora's repositories \u2026")
        for line in data.splitlines():
            self.details.appendPlainText(line)
            m = STEP_RE.match(line.strip())
            if m:
                n = int(m.group(1))
                self.bar.setValue(n - 1)
                self.status.setText(f"Step {n} of {STEPS}: {m.group(2)} …")

    def done(self, code, _status):
        self.output()
        self.running = False
        self.close_btn.setEnabled(True)
        if code in (126, 127):  # pkexec: dialog dismissed / not authorized
            self.stack.setCurrentIndex(0)
            QMessageBox.information(self, "Leave Ludora",
                                    "No password was given. Nothing was changed.")
            return
        if code == 0:
            self.bar.setValue(STEPS)
            self.status.setText(
                "<b>Done.</b> This is now Fedora KDE. Reboot to start Fedora's kernel."
                + (f"<br>At the next boot a blue screen asks you to delete the key: "
                   f"choose <i>Delete MOK</i>, confirm, and enter the password "
                   f"'{self.mok_password}'." if "--delete-key" in self.proc.arguments()
                   and "Deletion requested" in self.details.toPlainText() else ""))
            self.status.setTextFormat(Qt.TextFormat.RichText)
            self.reboot_btn.setVisible(True)
            self.reboot_btn.setDefault(True)
        else:
            self.status.setTextFormat(Qt.TextFormat.RichText)
            started = "==> 1/8" in self.details.toPlainText()
            self.status.setText(
                "<b>Leaving Ludora stopped with an error.</b> "
                + ("The steps already done stay done; open Leave Ludora again to "
                   "finish the rest. " if started else "Nothing was changed. ")
                + "The details are below and in /var/log/ludora-leave.log.")

    def reboot(self):
        QProcess.startDetached("systemctl", ["reboot"])

    def closeEvent(self, ev):
        if self.running:
            QMessageBox.information(self, "Leave Ludora",
                                    "Please wait until it has finished.")
            ev.ignore()
        else:
            ev.accept()


def main(mok_password):
    app = QApplication(sys.argv)
    app.setApplicationName("Leave Ludora")
    app.setDesktopFileName("ludora-leave")
    w = Window(mok_password)
    w.show()
    return app.exec()
