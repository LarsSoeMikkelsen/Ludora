Name:           calamares-config-ludora
Version:        1.8
Release:        26%{?dist}
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
install -Dm644 modules/shellprocess_relabel.conf %{buildroot}%{_sysconfdir}/calamares/modules/shellprocess_relabel.conf
install -Dm644 modules/users.conf          %{buildroot}%{_sysconfdir}/calamares/modules/users.conf
install -Dm644 modules/notesqml_secureboot.conf %{buildroot}%{_sysconfdir}/calamares/modules/notesqml_secureboot.conf
install -Dm644 qml/ludora-secureboot.qml    %{buildroot}%{_sysconfdir}/calamares/qml/ludora-secureboot.qml

# ludora_selections Python module (must be in libdir, not sysconfdir — Calamares
# only loads Python module code from /usr/lib64/calamares/modules/ on Fedora)
install -Dm644 modules/ludora_selections/module.desc \
    %{buildroot}%{_libdir}/calamares/modules/ludora_selections/module.desc
install -Dm644 modules/ludora_selections/main.py \
    %{buildroot}%{_libdir}/calamares/modules/ludora_selections/main.py
install -Dm644 modules/ludora_secureboot/module.desc \
    %{buildroot}%{_libdir}/calamares/modules/ludora_secureboot/module.desc
install -Dm644 modules/ludora_secureboot/main.py \
    %{buildroot}%{_libdir}/calamares/modules/ludora_secureboot/main.py

# Scripts
install -Dm755 scripts/packagechooser-cleanup.sh %{buildroot}%{_sysconfdir}/calamares/scripts/packagechooser-cleanup.sh
install -Dm755 scripts/ludora-grub-install %{buildroot}%{_sysconfdir}/calamares/scripts/ludora-grub-install
install -Dm755 scripts/ludora-sb-state %{buildroot}%{_sysconfdir}/calamares/scripts/ludora-sb-state

# Branding
install -Dm644 branding/branding.desc    %{buildroot}%{_sysconfdir}/calamares/branding/ludora/branding.desc
sed -i "s/@FEDORA_VERSION@/%{fedora}/g" %{buildroot}%{_sysconfdir}/calamares/branding/ludora/branding.desc
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
%{_sysconfdir}/calamares/modules/shellprocess_relabel.conf
%{_sysconfdir}/calamares/modules/users.conf
%{_sysconfdir}/calamares/modules/notesqml_secureboot.conf
%{_sysconfdir}/calamares/qml/ludora-secureboot.qml
%{_libdir}/calamares/modules/ludora_selections/module.desc
%{_libdir}/calamares/modules/ludora_selections/main.py
%{_libdir}/calamares/modules/ludora_secureboot/module.desc
%{_libdir}/calamares/modules/ludora_secureboot/main.py
%{_sysconfdir}/calamares/scripts/packagechooser-cleanup.sh
%{_sysconfdir}/calamares/scripts/ludora-grub-install
%{_sysconfdir}/calamares/scripts/ludora-sb-state
%{_sysconfdir}/calamares/branding/ludora/branding.desc
%{_sysconfdir}/calamares/branding/ludora/show.qml
%{_sysconfdir}/calamares/branding/ludora/logo.png
%{_sysconfdir}/calamares/branding/ludora/welcome.png

%changelog
* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-26
- shellprocess: run kernel-install add-all before dracut --regenerate-all.
  The ISO no longer has kernel-ludora's /boot/vmlinuz (so the live ISO boots
  Fedora's signed kernel); without it dracut picked the systemd-boot layout
  /boot/efi/<machine-id>/<kver>/ on UEFI installs and the install failed
  (beta8)

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-25
- Secure Boot page: import QtQuick.Controls.Basic. With the launcher's
  QT_STYLE_OVERRIDE=breeze the plain import wanted a "breeze" Qt Quick
  Controls style that is not installed, so the page failed to load (beta7)
- Secure Boot page: match the native pages (window background instead of
  white, system font and text colour, bold first line instead of a large
  heading)

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-24
- notesqml_secureboot.conf: the sidebar label key must be "notes". With
  "secureboot", notesqml left its label pointer uninitialised and Calamares
  crashed on startup (beta6)

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-23
- Secure Boot page (notesqml@secureboot, after Users), in the same 14
  languages as netinstall: with Secure Boot on, explains the one-time
  MokManager enrollment on first start step by step (password: ludora);
  with it off, says there is nothing to do
- ludora_secureboot job (after shellprocess): with Secure Boot on and a
  Ludora kernel installed, runs 'ludora-secureboot setup --password-stdin'
  in the target with the password "ludora". Never fails the installation
- ludora-sb-state: records the live Secure Boot state for the page (QML
  cannot run commands); called by the live session's calamares-launcher

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-22
- bootloader: boot through Fedora's signed shim instead of grub2-install on
  EFI (ludora-grub-install wrapper). grub2-install put an unsigned GRUB in
  \EFI\Ludora and pointed the boot entry at it, bypassing shim, so Secure
  Boot could never work. The "Ludora" entry now points at
  \EFI\fedora\shimx64.efi, with a grub.cfg stub for /boot/grub2/grub.cfg.
  BIOS installs still use grub2-install

* Sat Oct 17 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-21
- shellprocess@relabel: mount selinuxfs in the chroot before restorecon; without
  it restorecon saw SELinux as disabled and silently relabelled nothing (1.8-19
  fix was a no-op, found in the beta3 VM test)

* Sat Oct 17 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-20
- shellprocess: remove the live-only ludora-live-theme.desktop autostart entry
  from installed user homes (installed users get ludora-theme-apply.desktop
  from apply-ludora-theme-to-users.sh instead)

* Fri Oct 16 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-19
- add shellprocess@relabel after removeuser: restorecon the installed system
  (excluding /.snapshots). users/removeuser left /etc/passwd, shadow, group
  and gshadow labelled etc_t, so passwd failed even as root; installer-created
  subvolume roots were unlabeled_t

* Thu Oct 15 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-18
- partition: keep /boot unencrypted (noEncrypt) on encrypted installs; fixes
  double LUKS prompt and slow GRUB unlock (#7, #5)
- settings: add luksbootkeyfile + dracutlukscfg before fstab so manual
  layouts with an encrypted /boot get a single (GRUB) prompt; both are
  no-ops for the default layout

* Thu Oct 15 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.8-17
- branding.desc: take the version from %%{fedora} at build time instead of
  hard-coding 44, so F44 and F45 chroots each get the right "Ludora NN"

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
