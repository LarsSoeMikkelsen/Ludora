%global 	SHA256SUM0 46665282ea7ed65f3c1d7cc06afd0bb71be47b6b895105cd5e7c1af8a18370b1
%define         appid com.vysp3r.ProtonPlus

Name:           protonplus
Version:        0.6.4
Release:        1%{?dist}
Summary:        Simple and powerful manager for Wine, Proton, DXVK and VKD3D

ExclusiveArch:  x86_64
License:        GPL-3.0-or-later
URL:            https://github.com/vysp3r/ProtonPlus
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  fdupes
BuildRequires:  gettext
BuildRequires:  git-core
BuildRequires:  libappstream-glib
BuildRequires:  meson >= 1.0.0
BuildRequires:  ninja-build
BuildRequires:  vala
BuildRequires:  pkgconfig(appstream)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(gee-0.8)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.6
BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(sdl3) >= 3.2.0

# Need for TLS support
Requires:       glib-networking

%description
ProtonPlus is a simple and powerful manager for:
 - Wine
 - Proton
 - DXVK
 - VKD3D
 - Several other runners

Supports Steam, Lutris, Heroic and Bottles.

%prep
# echo "%SHA256SUM0 %{SOURCE0}" | sha256sum -c -
%autosetup -n ProtonPlus-%{version}

%build
%meson
%meson_build

%install
%meson_install
%find_lang %{appid}
# create symlinks for icons
# fix rpmlint W: files-duplicate
%fdupes -s %{buildroot}%{_datadir}/icons/hicolor

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop
appstream-util validate-relax --nonet \
    %{buildroot}%{_datadir}/metainfo/%{appid}.metainfo.xml

%files -f %{appid}.lang
%license LICENSE.md
%doc README.md CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md
%{_bindir}/protonplus
%{_datadir}/metainfo/%{appid}.metainfo.xml
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/glib-2.0/schemas/%{appid}.gschema.xml
%{_datadir}/icons/hicolor/*/apps/%{appid}.*
