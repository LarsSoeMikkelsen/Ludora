Name:           calamares-config-ludora
Version:        1.8
Release:        16%{?dist}
Summary:        Calamares installer configuration for Ludora Gaming Edition
License:        GPLv3+
URL:            https://ludora.org
Source0:        calamares-config-ludora-%{version}.tar.gz
BuildArch:      noarch
Requires:       calamares
Requires:       calamares-libs

%description
Calamares installer configuration for Ludora.
Provides module configs (bootloader, dracut, fstab, mount, partition,
netinstall, shellprocess, removeuser) and Ludora branding
for the Calamares installer.
The mount module config sets up the Btrfs subvolume layout used by Ludora.
The netinstall module lets users select optional components at install time.
The ludora_selections Python module bridges netinstall selections to the
shellprocess cleanup script, which removes unselected packages from the
pre-installed squashfs image.

%define debug_package %{nil}

%prep
%setup -q -n calamares-config-ludora-%{version}

%build
# Nothing to build

%install
# settings.conf
install -Dm644 settings.conf %{buildroot}%{_sysconfdir}/calamares/settings.conf

# Module configs
install -Dm644 modules/bootloader.conf      %{buildroot}%{_sysconfdir}/calamares/modules/bootloader.conf
install -Dm644 modules/dracut.conf          %{buildroot}%{_sysconfdir}/calamares/modules/dracut.conf
install -Dm644 modules/fstab.conf           %{buildroot}%{_sysconfdir}/calamares/modules/fstab.conf
install -Dm644 modules/mount.conf           %{buildroot}%{_sysconfdir}/calamares/modules/mount.conf
install -Dm644 modules/netinstall.conf      %{buildroot}%{_sysconfdir}/calamares/modules/netinstall.conf
install -Dm644 modules/partition.conf       %{buildroot}%{_sysconfdir}/calamares/modules/partition.conf
install -Dm644 modules/removeuser.conf      %{buildroot}%{_sysconfdir}/calamares/modules/removeuser.conf
install -Dm644 modules/shellprocess.conf    %{buildroot}%{_sysconfdir}/calamares/modules/shellprocess.conf
install -Dm644 modules/users.conf          %{buildroot}%{_sysconfdir}/calamares/modules/users.conf

# ludora_selections Python module (must be in libdir, not sysconfdir — Calamares
# only loads Python module code from /usr/lib64/calamares/modules/ on Fedora)
install -Dm644 modules/ludora_selections/module.desc \
    %{buildroot}%{_libdir}/calamares/modules/ludora_selections/module.desc
install -Dm644 modules/ludora_selections/main.py \
    %{buildroot}%{_libdir}/calamares/modules/ludora_selections/main.py

# Scripts
install -Dm755 scripts/packagechooser-cleanup.sh %{buildroot}%{_sysconfdir}/calamares/scripts/packagechooser-cleanup.sh

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
%{_sysconfdir}/calamares/modules/netinstall.conf
%{_sysconfdir}/calamares/modules/partition.conf
%{_sysconfdir}/calamares/modules/removeuser.conf
%{_sysconfdir}/calamares/modules/shellprocess.conf
%{_sysconfdir}/calamares/modules/users.conf
%{_libdir}/calamares/modules/ludora_selections/module.desc
%{_libdir}/calamares/modules/ludora_selections/main.py
%{_sysconfdir}/calamares/scripts/packagechooser-cleanup.sh
%{_sysconfdir}/calamares/branding/ludora/branding.desc
%{_sysconfdir}/calamares/branding/ludora/show.qml
%{_sysconfdir}/calamares/branding/ludora/logo.png
%{_sysconfdir}/calamares/branding/ludora/welcome.png

%changelog
* Wed May 13 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-15
- Remove ludora-welcome from netinstall packages; pulled in as dep of kde-ludora

* Thu May 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-14
- Remove vulkan-tools from Gaming Stack cleanup and netinstall.conf:
  kinfocenter hard-depends on it, so removing it forces kinfocenter out
  as a reverse dependency when Gaming Stack is deselected

* Thu May 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-13
- shellprocess.conf: remove calamares, calamares-libs, calamares-config-ludora
  from the installed system at the end of post-install steps

* Thu May 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-12
- users.conf: drop libpwquality block — libpwquality enforces a hardcoded
  floor of 6 characters even with minlen=0, so omitting the block skips
  strength checking and lets minLength: 0 take full effect

* Thu May 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-11
- Add users.conf: override Fedora system pwquality.conf (minlen=10) with
  minLength=0 and libpwquality minlen=0/minclass=0 to remove password
  length enforcement in the installer

* Thu May 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-10
- Fix missing SDDM when Multimedia Codecs are deselected: remove
  gstreamer1-plugins-base from the codec cleanup list — sddm depends on it,
  so removing it forces sddm out as a reverse dependency

* Wed May 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-9
- Fix missing SDDM when Ludora Custom KDE is deselected: mark sddm and
  plasma-workspace as explicitly installed before removing kde-ludora so
  they are not removed as orphaned dependencies

* Wed May 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-8
- Fix dracut failure when kernel-ludora is deselected: remove dracut from
  Calamares exec sequence and run dracut --regenerate-all --force from
  shellprocess.conf after cleanup, so initramfs is built for whichever
  kernel actually remains on the installed system

* Wed May 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-7
- Fix packagechooser-cleanup.sh: deselecting all components now correctly
  removes all optional packages instead of keeping everything

* Tue May 06 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-6
- Add netinstall translations for 14 languages (de, fr, es, it, pt, zh_CN, ja,
  ko, pl, nl, da, fi, nb, sv) covering label, group names and descriptions
- Remove unused packagechooser.conf and packages.conf

* Wed May 06 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-5
- Rename netinstall groups to "Ludora Custom KDE" and "Ludora Custom Kernel"
- Move Ludora Custom KDE above Ludora Custom Kernel in group order
- Shorten Ludora Custom Kernel description
- Set all netinstall groups to critical: true

* Wed May 06 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-4
- Skip apply-ludora-theme-to-users.sh gracefully when Ludora KDE customizations
  are not selected (script absent); guard with existence check in shellprocess.conf

* Tue May 05 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-3
- Fix kernel removal: add --setopt=protect_running_kernel=false so DNF removes
  kernel-ludora even when the live ISO is running it
- Ludora Desktop Customization is now all-or-nothing (only kde-ludora listed
  in netinstall, cleanup removes all four packages as a unit)

* Tue May 05 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-2
- Fix ludora_selections module path: install to %%{_libdir}/calamares/modules/
  instead of %%{_sysconfdir} — Calamares on Fedora loads Python module code
  from /usr/lib64/calamares/modules/, not /etc/calamares/modules/

* Tue May 05 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-1
- Replace packagechooser with netinstall for component selection UI
- Add ludora_selections Python module to bridge netinstall selections to cleanup
- Update packagechooser-cleanup.sh to read selections from /tmp/ludora-selections
- Update shellprocess.conf to call cleanup without arguments
- Remove packages module from exec sequence (squashfs approach, no net installs)

* Sun May 04 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.7-1
- Add packagechooser module for optional component selection at install time
- Add packages, shellprocess, removeuser module configs
- Add packagechooser-cleanup.sh script for removing unselected packages
- Move shellprocess.conf from kickstart %%post into package

* Tue Mar 10 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-1
- Initial release
