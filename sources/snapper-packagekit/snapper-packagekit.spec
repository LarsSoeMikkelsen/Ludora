Name:           snapper-packagekit
Version:        1.0
Release:        1%{?dist}
Summary:        Automatic snapper pre/post snapshots for PackageKit transactions
License:        GPLv3+
URL:            https://ludora.org
Source0:        snapper-packagekit-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  systemd-rpm-macros
Requires:       snapper
Requires:       python3-dbus
Requires:       python3-gobject
Requires:       PackageKit

%description
Watches PackageKit over D-Bus and creates snapper pre/post snapshot pairs
around any install, update, or remove transaction. This covers software
installed through KDE Discover or any other PackageKit frontend.

%define debug_package %{nil}

%prep
%setup -q -n snapper-packagekit-%{version}

%build
# Nothing to build

%install
install -Dm755 snapper-packagekit \
    %{buildroot}%{_bindir}/snapper-packagekit

install -Dm644 snapper-packagekit.service \
    %{buildroot}/usr/lib/systemd/system/snapper-packagekit.service

%post
%systemd_post snapper-packagekit.service

%preun
%systemd_preun snapper-packagekit.service

%postun
%systemd_postun snapper-packagekit.service

%files
%{_bindir}/snapper-packagekit
/usr/lib/systemd/system/snapper-packagekit.service

%changelog
* Sun Jul 06 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-1
- Initial release
