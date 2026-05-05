import libcalamares
import os


def run():
    root = libcalamares.globalstorage.value("rootMountPoint")
    if not root:
        return ("No rootMountPoint", "Cannot determine install root")

    ops = libcalamares.globalstorage.value("packageOperations")
    selected = []
    if ops:
        for op in ops:
            if isinstance(op, dict):
                for key in ("install", "try_install"):
                    pkgs = op.get(key, [])
                    if pkgs:
                        selected.extend(str(p) for p in pkgs)

    os.makedirs(os.path.join(root, "tmp"), exist_ok=True)
    with open(os.path.join(root, "tmp", "ludora-selections"), "w") as f:
        f.write("\n".join(selected) + "\n")

    return None
