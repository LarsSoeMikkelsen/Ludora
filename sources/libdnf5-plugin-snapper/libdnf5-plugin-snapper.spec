Name:           libdnf5-plugin-snapper
Version:        1.0.2
Release:        1%{?dist}
Summary:        Snapper plugin for DNF5 - automatic filesystem snapshots

License:        LGPL-2.1-or-later
Source0:        https://github.com/Plenvorik/libdnf5-plugin-snapper/releases/download/v%{version}/libdnf5-plugin-snapper-%{version}.tar.gz

BuildRequires:  cmake >= 3.18
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(libdnf5) >= 5.0
BuildRequires:  snapper-devel >= 0.10
BuildRequires:  boost-devel >= 1.54
BuildRequires:  pkgconfig(fmt)
BuildRequires:  catch2-devel

Requires:       libdnf5%{?_isa} >= 5.0
Requires:       snapper-libs%{?_isa} >= 0.10
Requires:       dnf5

# Suggests the old plugin should be removed if installed
Obsoletes:      python3-dnf-plugin-snapper < 5.0
Provides:       dnf5-plugin-snapper = %{version}-%{release}

%description
This plugin extends DNF5 to automatically create snapper snapshots before and
after package transactions. It provides rollback capabilities and system state
tracking through filesystem snapshots.

Features:
- Automatic pre/post transaction snapshots
- Direct libsnapper API integration (no D-Bus required)
- Package filtering for selective snapshots
- Important packages marking

%prep
%autosetup -p1

%build
%cmake \
    -DLIBDNF5_PLUGIN_DIR=%{_libdir}/libdnf5/plugins \
    -DPLUGIN_CONF_DIR=%{_sysconfdir}/dnf/libdnf5-plugins

%cmake_build

%install
%cmake_install

%check
%ctest

%files
%license COPYING
%doc README.md
%doc CHANGELOG.md
%dir %{_sysconfdir}/dnf/libdnf5-plugins
%config(noreplace) %{_sysconfdir}/dnf/libdnf5-plugins/snapper.conf
%{_libdir}/libdnf5/plugins/snapper.so

%changelog
* Wed Nov 26 2025 Andre Herrlich <plenvorik@gmail.com> - 1.0.2-1
- Add Fedora 43 support
- Update CI workflow for Fedora 43

* Wed Oct 08 2025 Andre Herrlich <plenvorik@gmail.com> - 1.0.1-1
- Code cleanup and fix snapshot read-only behavior

* Tue Sep 30 2025 Andre Herrlich <plenvorik@gmail.com> - 1.0.0-1
- Initial release with automatic pre/post transaction snapshots via libsnapper API
