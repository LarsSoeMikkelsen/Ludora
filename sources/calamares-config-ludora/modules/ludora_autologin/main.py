# Autologin for Plasma Login Manager.
#
# Calamares' displaymanager module doesn't know plasmalogin (the login manager
# since F44), so the users page's "Log in automatically" box had no effect.
# Write the same [Autologin] section livesys-kde uses for the live session,
# as a drop-in so /etc/plasmalogin.conf stays package-owned.
import os

import libcalamares

DROPIN = "etc/plasmalogin.conf.d/50-ludora-autologin.conf"
SESSION = "plasma.desktop"


def run():
    root = libcalamares.globalstorage.value("rootMountPoint")
    if not root:
        return ("No rootMountPoint", "Cannot determine install root")

    path = os.path.join(root, DROPIN)
    user = libcalamares.globalstorage.value("autoLoginUser")
    if not user:
        if os.path.exists(path):
            os.remove(path)
        libcalamares.utils.debug("ludora_autologin: autologin not requested")
        return None

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("[Autologin]\nUser={}\nSession={}\n".format(user, SESSION))
    os.chmod(path, 0o644)
    libcalamares.utils.debug("ludora_autologin: autologin for {}".format(user))
    return None
