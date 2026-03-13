Name:           calamares-config-ludora
Version:        1.2
Release:        1%{?dist}
Summary:        Calamares installer configuration for Ludora Gaming Edition
License:        GPLv3+
URL:            https://ludora.org
Source0:        calamares-config-ludora-%{version}.tar.gz
BuildArch:      noarch
Requires:       calamares
Requires:       calamares-libs

%description
Calamares installer configuration for Ludora Gaming Edition.
Provides module configs (bootloader, dracut, fstab, mount, partition,
removeuser) and Ludora branding for the Calamares installer.
The mount module config sets up the Btrfs subvolume layout used by Ludora.

%define debug_package %{nil}

%prep
%setup -q -n calamares-config-ludora-%{version}

%build
# Nothing to build

%install
# settings.conf
install -Dm644 settings.conf %{buildroot}%{_sysconfdir}/calamares/settings.conf

# Module configs
install -Dm644 modules/bootloader.conf   %{buildroot}%{_sysconfdir}/calamares/modules/bootloader.conf
install -Dm644 modules/dracut.conf       %{buildroot}%{_sysconfdir}/calamares/modules/dracut.conf
install -Dm644 modules/fstab.conf        %{buildroot}%{_sysconfdir}/calamares/modules/fstab.conf
install -Dm644 modules/mount.conf        %{buildroot}%{_sysconfdir}/calamares/modules/mount.conf
install -Dm644 modules/partition.conf    %{buildroot}%{_sysconfdir}/calamares/modules/partition.conf
install -Dm644 modules/removeuser.conf   %{buildroot}%{_sysconfdir}/calamares/modules/removeuser.conf

# Branding
install -Dm644 branding/branding.desc    %{buildroot}%{_sysconfdir}/calamares/branding/ludora/branding.desc
install -Dm644 branding/show.qml         %{buildroot}%{_sysconfdir}/calamares/branding/ludora/show.qml
install -Dm644 branding/logo.png         %{buildroot}%{_sysconfdir}/calamares/branding/ludora/logo.png
install -Dm644 branding/welcome.png      %{buildroot}%{_sysconfdir}/calamares/branding/ludora/welcome.png

%files
%{_sysconfdir}/calamares/settings.conf
%{_sysconfdir}/calamares/modules/bootloader.conf
%{_sysconfdir}/calamares/modules/dracut.conf
%{_sysconfdir}/calamares/modules/fstab.conf
%{_sysconfdir}/calamares/modules/mount.conf
%{_sysconfdir}/calamares/modules/partition.conf
%{_sysconfdir}/calamares/modules/removeuser.conf
%{_sysconfdir}/calamares/branding/ludora/branding.desc
%{_sysconfdir}/calamares/branding/ludora/show.qml
%{_sysconfdir}/calamares/branding/ludora/logo.png
%{_sysconfdir}/calamares/branding/ludora/welcome.png

%changelog
* Tue Mar 10 2026 Ludora Team <team@ludora.org> - 1.0-1
- Initial release
