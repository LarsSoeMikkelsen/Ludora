"""Set up Secure Boot signing on the installed system.

Never fails the installation (see the end of run()).

When the live system booted with Secure Boot on and kernel-ludora was
installed, run 'ludora-secureboot setup' in the target: per-machine key,
signed kernels, akmods key, and a queued MOK enrollment with the
one-time password "ludora", which the Secure Boot page tells the user.
Runs after shellprocess, so kernel-install has already put the final
kernels in /boot.
"""
import glob
import os
import subprocess

import libcalamares

INI = "/tmp/ludora-secureboot.ini"
# Fixed on purpose; shown on the Secure Boot page in every language
MOK_PASSWORD = "ludora"


def pretty_name():
    return "Setting up Secure Boot signing."


def secure_boot_enabled():
    try:
        out = subprocess.run(["mokutil", "--sb-state"], capture_output=True,
                             text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return "SecureBoot enabled" in out


def run_logged(command, stdin, timeout):
    """Run command in the target with its output in the session log.

    Returns the exit code (-1 if it could not be run)."""
    name = command[0] + " " + command[1]

    def log_line(line):
        libcalamares.utils.debug("{}: {}".format(name, line.rstrip()))

    try:
        return libcalamares.utils.target_env_process_output(
            command, log_line, stdin, timeout)
    except subprocess.CalledProcessError as e:
        return e.returncode
    except Exception as e:  # timeout or anything else: never fail the job
        libcalamares.utils.warning("{} failed: {}".format(name, e))
        return -1


def run():
    if not secure_boot_enabled():
        libcalamares.utils.debug("ludora_secureboot: Secure Boot off, skipping")
        return None

    root = libcalamares.globalstorage.value("rootMountPoint")
    if not root:
        return ("No rootMountPoint", "Cannot determine install root")

    if not glob.glob(os.path.join(root, "usr/lib/modules/*ludora*")):
        libcalamares.utils.debug("ludora_secureboot: no Ludora kernel installed "
                                 "(Fedora's signed kernel boots as is), skipping")
        return None

    if not os.path.exists(os.path.join(root, "usr/sbin/ludora-secureboot")):
        libcalamares.utils.warning("ludora_secureboot: ludora-secureboot not in the "
                                   "image, Ludora kernel left unsigned")
        return None

    rc = run_logged(["ludora-secureboot", "setup", "--password-stdin"],
                    MOK_PASSWORD + "\n", 300)
    # Record the result (key, MOK pending/enrolled, kernel signatures) in
    # the session log, which preservefiles copies to the installed system
    run_logged(["ludora-secureboot", "status"], "", 60)

    try:
        os.remove(INI)
    except OSError:
        pass

    # Never fail the job: that would abort the installation before removeuser
    # and the SELinux relabel run. The Secure Boot page explains the recovery
    # (Fedora's kernel boots; 'sudo ludora-secureboot setup', reboot).
    if rc != 0:
        libcalamares.utils.warning(
            "ludora_secureboot: 'ludora-secureboot setup' exited with {}".format(rc))
    return None
