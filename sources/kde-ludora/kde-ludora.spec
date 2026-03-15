Name:           kde-ludora
Version:        1.5
Release:        1%{?dist}
Summary:        Ludora KDE Plasma Global Theme
License:        GPLv2+
URL:            https://ludora.org
Source0:        kde-ludora-%{version}.tar.gz
BuildArch:      noarch
Requires:       plasma-workspace
Requires:       papirus-icon-theme

%description
Ludora is a KDE Plasma global theme for the Ludora gaming Linux distribution.
Based on Breeze Dark with a custom amber accent color scheme, centered taskbar,
icons-only task manager, Papirus-Dark icons, and Ludora branding.

%define debug_package %{nil}

%prep
%setup -T -b 0 -q -n kde-ludora-%{version}

%build
# Nothing to build

%install
# Install look-and-feel theme
mkdir -p %{buildroot}%{_datadir}/plasma/look-and-feel/org.ludora.desktop
cp -ar look-and-feel/* %{buildroot}%{_datadir}/plasma/look-and-feel/org.ludora.desktop/

# Install color scheme
mkdir -p %{buildroot}%{_datadir}/color-schemes
cp color-schemes/Ludora.colors %{buildroot}%{_datadir}/color-schemes/

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
cp icons/scalable/ludora-start-here.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/
cp icons/64x64/ludora-start-here.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/
cp icons/128x128/ludora-start-here.svg %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/
cp icons/256x256/ludora-start-here.svg %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/

%files
%{_datadir}/plasma/look-and-feel/org.ludora.desktop/
%{_datadir}/color-schemes/Ludora.colors
%{_datadir}/icons/hicolor/scalable/apps/ludora-start-here.svg
%{_datadir}/icons/hicolor/64x64/apps/ludora-start-here.png
%{_datadir}/icons/hicolor/128x128/apps/ludora-start-here.svg
%{_datadir}/icons/hicolor/256x256/apps/ludora-start-here.svg

%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
* Thu Feb 26 2026 Ludora Team <team@ludora.org> - 1.1-1
- Add custom Ludora amber color scheme replacing Breeze Dark blue accent
- Update panel layout: centered taskbar, icons-only task manager, proper spacers
- Fix kickoff launcher icon to use theme name instead of hardcoded path
- Update metadata with website and description
- Remove wallpaper package (wallpaper handled separately)

* Mon Feb 24 2025 Ludora Team <team@ludora.org> - 1.0-1
- Initial release of Ludora KDE theme
