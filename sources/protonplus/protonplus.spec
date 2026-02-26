%global 	SHA256SUM0 2ed82b873b154033b4790a496887bf7098dfea1dfa3253827aad1879de82db4a
%define         appid com.vysp3r.ProtonPlus

Name:           protonplus
Version:        0.5.17
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
BuildRequires:  pkgconfig(gee-0.8)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.5.0
BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(libsoup-3.0)

# Need for TLS support
Requires:       glib-networking

Obsoletes:  	protonup-qt
Obsoletes:	protonplus-next

%description
ProtonPlus is a simple and powerful manager for:
 - Wine
 - Proton
 - DXVK
 - VKD3D
 - Several other runners

Supports Steam, Lutris, Heroic and Bottles.

%prep
echo "%SHA256SUM0 %{SOURCE0}" | sha256sum -c -
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
