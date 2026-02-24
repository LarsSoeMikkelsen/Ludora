Name:           kde-ludora
Version:        1.0
Release:        1%{?dist}
Summary:        Ludora KDE Plasma Global Theme

License:        GPLv2+
URL:            https://github.com/LarsSoeMikkelsen/Ludora/tree/main/sources/kde-ludora

BuildArch:      noarch

Requires:       plasma-workspace
Requires:       papirus-icon-theme

%description
Ludora is a KDE Plasma global theme based on Breeze Dark with Papirus icons,
featuring custom wallpapers and branding for the Ludora distribution.

%prep
# No prep needed - files are in the repo

%build
# Nothing to build

%install
# Install look-and-feel theme
mkdir -p %{buildroot}%{_datadir}/plasma/look-and-feel/org.ludora.desktop
cp -ar %{_builddir}/kde-ludora/look-and-feel/* %{buildroot}%{_datadir}/plasma/look-and-feel/org.ludora.desktop/

# Install wallpaper
mkdir -p %{buildroot}%{_datadir}/wallpapers/Ludora
cp -ar %{_builddir}/kde-ludora/wallpaper/* %{buildroot}%{_datadir}/wallpapers/Ludora/

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps

cp %{_builddir}/kde-ludora/icons/scalable/ludora-start-here.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/
cp %{_builddir}/kde-ludora/icons/64x64/ludora-start-here.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/
cp %{_builddir}/kde-ludora/icons/128x128/ludora-start-here.svg %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/
cp %{_builddir}/kde-ludora/icons/256x256/ludora-start-here.svg %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/

%files
%{_datadir}/plasma/look-and-feel/org.ludora.desktop/
%{_datadir}/wallpapers/Ludora/
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
* Mon Feb 24 2026 Ludora Team <team@ludora.org> - 1.0-1
- Initial release of Ludora KDE theme
- Uses Papirus-Dark icon theme
