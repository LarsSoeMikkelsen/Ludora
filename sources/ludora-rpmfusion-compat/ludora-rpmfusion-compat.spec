Name:           ludora-rpmfusion-compat
Version:        1.0
Release:        1%{?dist}
Summary:        Work around unresolvable dependency in RPM Fusion F45 release packages
License:        MIT
URL:            https://github.com/LarsSoeMikkelsen/Ludora
BuildArch:      noarch

# rpmfusion-{free,nonfree}-release-45-1 require "/usr/share/dnf5/libdnf.conf.d/"
# with a trailing slash. libdnf5 owns the directory without the slash, so the
# requirement never resolves and the release packages cannot be installed
# (@core pulls them in via RPM Fusion comps, so this breaks the ISO build).
# The directory really exists on every system (libdnf5 owns it); this only
# provides the misspelled path.
#
# Do NOT drop this provide while 45-1 can still be installed: removing this
# package cascade-removes both RPM Fusion release packages. Remove only after
# a fixed rpmfusion-*-release has been in releases/updates for F45 and every
# later Fedora release Ludora supports.
Provides:       /usr/share/dnf5/libdnf.conf.d/

%description
Provides the path "/usr/share/dnf5/libdnf.conf.d/" (with trailing slash)
required by rpmfusion-free-release and rpmfusion-nonfree-release 45-1, which
otherwise cannot be installed. Contains no files.

%prep

%build

%install

%files

%changelog
* Tue Nov 03 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-1
- Initial package: provide the trailing-slash libdnf.conf.d path required by
  rpmfusion-{free,nonfree}-release-45-1
