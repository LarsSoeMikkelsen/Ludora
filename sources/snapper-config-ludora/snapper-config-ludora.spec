Name:           snapper-config-ludora
Version:        1.9
Release:        5%{?dist}
Summary:        Snapper first-boot setup and rollback wrapper for Ludora Gaming Edition
License:        GPLv3+
URL:            https://ludora.org
Source0:        snapper-config-ludora-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  systemd-rpm-macros
Requires:       snapper
Requires:       grub-btrfs
Requires:       btrfs-progs
Requires:       kdialog
Requires:       konsole

%description
Provides first-boot snapper configuration for Ludora Gaming Edition.
Installs a oneshot systemd service that runs on first boot to:
  - Create the snapper root config and /.snapshots subvolume
  - Set /@ as the default Btrfs subvolume (required for snapper rollback)
  - Tune snapshot retention limits
  - Add /.snapshots to fstab and enable grub-btrfs
  - Create an initial snapshot
Also includes:
  - snapper-rollback: wrapper calling 'snapper --ambit classic rollback'
  - snapper-commit: make booted snapshot permanent (CachyOS-style workflow)
  - Automatic snapshot boot detection with KDE notification popup
  - Desktop launcher for manual snapshot commit

%define debug_package %{nil}

%prep
%setup -q -n snapper-config-ludora-%{version}

%build
# Nothing to build

%install
# First-boot service
install -Dm644 ludora-snapper-setup.service \
    %{buildroot}/usr/lib/systemd/system/ludora-snapper-setup.service

# Completion marker of the first-boot setup (%ghost: created at runtime)
install -d %{buildroot}/var/lib/ludora
touch %{buildroot}/var/lib/ludora/snapper-setup.done

# First-boot setup script
install -Dm755 ludora-snapper-setup.sh \
    %{buildroot}/usr/local/bin/ludora-snapper-setup.sh

# Snapshot commit script
install -Dm755 snapper-commit \
    %{buildroot}/usr/local/bin/snapper-commit

# Snapshot detection notification script
install -Dm755 ludora-snapshot-notify.sh \
    %{buildroot}/usr/local/bin/ludora-snapshot-notify.sh

# Autostart desktop file for notification
install -Dm644 ludora-snapshot-notify.desktop \
    %{buildroot}/etc/xdg/autostart/ludora-snapshot-notify.desktop

# Desktop launcher for manual commit
install -Dm644 ludora-snapshot-commit.desktop \
    %{buildroot}/usr/share/applications/ludora-snapshot-commit.desktop

%post
%systemd_post ludora-snapper-setup.service
if [ $1 -eq 1 ]; then
    systemctl enable ludora-snapper-setup.service &>/dev/null || :
elif [ ! -e /var/lib/ludora/snapper-setup.done ] && [ -e /etc/snapper/configs/root ]; then
    # Upgrade from <= 1.9-4, which used the snapper config as its "done"
    # marker. Finished setups (/.snapshots in fstab) get the new marker;
    # ones that failed after create-config are finished on the next boot.
    if awk '$1 !~ /^#/ && $2=="/.snapshots" {f=1} END {exit !f}' /etc/fstab; then
        mkdir -p /var/lib/ludora && touch /var/lib/ludora/snapper-setup.done
    else
        systemctl enable ludora-snapper-setup.service &>/dev/null || :
    fi
fi

%preun
%systemd_preun ludora-snapper-setup.service

%postun
%systemd_postun ludora-snapper-setup.service

%files
/usr/lib/systemd/system/ludora-snapper-setup.service
/usr/local/bin/ludora-snapper-setup.sh
/usr/local/bin/snapper-commit
/usr/local/bin/ludora-snapshot-notify.sh
/etc/xdg/autostart/ludora-snapshot-notify.desktop
/usr/share/applications/ludora-snapshot-commit.desktop
%dir /var/lib/ludora
%ghost /var/lib/ludora/snapper-setup.done

%changelog
* Fri Nov 13 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.9-5
- ludora-snapper-setup: retried on the next boot when a step fails (done
  marker /var/lib/ludora/snapper-setup.done written last; the snapper config
  used to count as done, so a failure after create-config was permanent);
  every step skips work already done (no duplicate /.snapshots fstab line or
  initial snapshot); a non-Btrfs root is a clean no-op instead of a failure
  on every boot; no longer deletes its own packaged files
- Enable the setup unit only on first install; upgrades mark finished setups
  done and finish ones that failed part-way

* Mon Nov 09 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.9-4
- ludora-snapper-setup: regenerate grub.cfg through grub-btrfs.service
  instead of a second grub2-mkconfig; both ran at once on first boot and
  grub-btrfs.service failed, leaving the system degraded

* Tue Nov 03 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.9-3
- snapper-commit: only rebuild initramfs for kernels whose modules exist in
  the committed root, and set the GRUB default to such a kernel; rolling back
  past a kernel update (separate /boot) left a module-less kernel as default
  and the next boot ended in emergency mode

* Tue Nov 03 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.9-2
- Add BuildRequires: systemd-rpm-macros; the %%systemd_* scriptlet macros were
  never expanded, so %%preun failed on every upgrade/removal and left the old
  package installed alongside the new one

* Tue Oct 13 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.9-1
- Fix /.snapshots fstab entry on encrypted installs (reuse root device verbatim
  instead of assuming UUID=); mount only /.snapshots instead of mount -a

* Thu Mar 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-3
- Add snapper-commit script for CachyOS-style snapshot workflow
- Add automatic KDE notification when booted into snapshot
- Add desktop launcher for manual snapshot commit
- Add kdialog and konsole dependencies

* Tue Mar 10 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-2
- Fix ConditionPathExists in systemd service

* Tue Mar 10 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-1
- Initial release
