Name:           snapper-actions-ludora
Version:        1.0
Release:        1%{?dist}
Summary:        DNF5 automatic snapper snapshots for Ludora Gaming Edition
License:        GPLv3+
URL:            https://ludora.org
Source0:        snapper-actions-ludora-%{version}.tar.gz
BuildArch:      noarch
Requires:       libdnf5-plugin-actions
Requires:       snapper
Requires:       grub-btrfs

%description
Configures automatic pre/post Btrfs snapshots for all DNF5 transactions
on Ludora Gaming Edition. Uses the libdnf5-plugin-actions mechanism to
call snapper before and after each transaction.
Important packages (kernel, Mesa, Vulkan, systemd, grub2, firmware, ROCm)
are marked with Userdata "important=yes" in the snapshot list.
Also installs the Fedora-specific grub-btrfs configuration.

%define debug_package %{nil}

%prep
%setup -q -n snapper-actions-ludora-%{version}

%build
# Nothing to build

%install
# DNF5 actions plugin config
install -Dm644 actions.conf \
    %{buildroot}%{_sysconfdir}/dnf/libdnf5-plugins/actions.conf

# Snapper actions file
install -Dm644 snapper.actions \
    %{buildroot}%{_sysconfdir}/dnf/libdnf5-plugins/actions.d/snapper.actions

# grub-btrfs Fedora-specific config
install -Dm644 grub-btrfs-config \
    %{buildroot}%{_sysconfdir}/default/grub-btrfs/config

%files
%{_sysconfdir}/dnf/libdnf5-plugins/actions.conf
%{_sysconfdir}/dnf/libdnf5-plugins/actions.d/snapper.actions
%{_sysconfdir}/default/grub-btrfs/config

%changelog
* Tue Mar 10 2026 Ludora Team <team@ludora.org> - 1.0-1
- Initial release
