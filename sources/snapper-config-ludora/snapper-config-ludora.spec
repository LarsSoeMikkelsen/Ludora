Name:           snapper-config-ludora
Version:        1.0
Release:        1%{?dist}
Summary:        Snapper first-boot setup and rollback wrapper for Ludora Gaming Edition
License:        GPLv3+
URL:            https://ludora.org
Source0:        snapper-config-ludora-%{version}.tar.gz
BuildArch:      noarch
Requires:       snapper
Requires:       grub-btrfs
Requires:       btrfs-progs

%description
Provides first-boot snapper configuration for Ludora Gaming Edition.
Installs a oneshot systemd service that runs on first boot to:
  - Create the snapper root config and /.snapshots subvolume
  - Set /@ as the default Btrfs subvolume (required for snapper rollback)
  - Tune snapshot retention limits
  - Add /.snapshots to fstab and enable grub-btrfs
  - Create an initial snapshot
Also installs snapper-rollback, a wrapper that calls
'snapper --ambit classic rollback' since Fedora uses @ as the default
subvolume rather than a snapshot subvolume.

%define debug_package %{nil}

%prep
%setup -q -n snapper-config-ludora-%{version}

%build
# Nothing to build

%install
# First-boot service
install -Dm644 ludora-snapper-setup.service \
    %{buildroot}/usr/lib/systemd/system/ludora-snapper-setup.service

# First-boot setup script
install -Dm755 ludora-snapper-setup.sh \
    %{buildroot}/usr/local/bin/ludora-snapper-setup.sh

# Rollback wrapper
install -Dm755 snapper-rollback \
    %{buildroot}/usr/local/bin/snapper-rollback

%post
%systemd_post ludora-snapper-setup.service
systemctl enable ludora-snapper-setup.service &>/dev/null || :

%preun
%systemd_preun ludora-snapper-setup.service

%postun
%systemd_postun ludora-snapper-setup.service

%files
/usr/lib/systemd/system/ludora-snapper-setup.service
/usr/local/bin/ludora-snapper-setup.sh
/usr/local/bin/snapper-rollback

%changelog
* Tue Mar 10 2026 Ludora Team <team@ludora.org> - 1.0-1
- Initial release
