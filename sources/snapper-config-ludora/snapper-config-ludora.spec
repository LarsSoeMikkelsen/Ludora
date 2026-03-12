Name:           snapper-config-ludora
Version:        1.3
Release:        1%{?dist}
Summary:        Snapper first-boot setup and rollback wrapper for Ludora Gaming Edition
License:        GPLv3+
URL:            https://ludora.org
Source0:        snapper-config-ludora-%{version}.tar.gz
BuildArch:      noarch
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
    %{buildroot}%{_unitdir}/ludora-snapper-setup.service

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
systemctl enable ludora-snapper-setup.service &>/dev/null || :

%preun
%systemd_preun ludora-snapper-setup.service

%postun
%systemd_postun ludora-snapper-setup.service

%files
%{_unitdir}/ludora-snapper-setup.service
/usr/local/bin/ludora-snapper-setup.sh
/usr/local/bin/snapper-rollback
/usr/local/bin/snapper-commit
/usr/local/bin/ludora-snapshot-notify.sh
/etc/xdg/autostart/ludora-snapshot-notify.desktop
/usr/share/applications/ludora-snapshot-commit.desktop

%changelog
* Thu Mar 12 2026 Ludora Team <team@ludora.org> - 1.0-3
- Add snapper-commit script for CachyOS-style snapshot workflow
- Add automatic KDE notification when booted into snapshot
- Add desktop launcher for manual snapshot commit
- Add kdialog and konsole dependencies

* Tue Mar 10 2026 Ludora Team <team@ludora.org> - 1.0-2
- Fix ConditionPathExists in systemd service

* Tue Mar 10 2026 Ludora Team <team@ludora.org> - 1.0-1
- Initial release
