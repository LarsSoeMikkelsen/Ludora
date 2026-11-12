Name:           desktop-defaults-ludora
Version:        1.1
Release:        7%{?dist}
Summary:        KDE desktop defaults and system configuration for Ludora
License:        GPLv3+
URL:            https://ludora.org
Source0:        desktop-defaults-ludora-%{version}.tar.gz
BuildArch:      noarch
Requires:       kde-ludora
Requires:       fastfetch
Requires:       polkit
# Every Ludora system gets the way back to plain Fedora KDE
Requires:       ludora-leave
Requires(post): coreutils grep
# Its only file is /etc/xdg/discoverrc (UseOfflineUpdates=true). Discover's
# offline updates are not snapshotted by libdnf5-plugin-snapper; online
# PackageKit transactions are. Users can still pick "after restart" in
# System Settings > Software Update (per-user discoverrc wins).
Obsoletes:      plasma-discover-offline-updates

%description
System-wide desktop defaults for Ludora Gaming Edition.
  - fastfetch display on interactive shell startup (via profile.d)
  - Theme application scripts for new users on first login

%define debug_package %{nil}

%prep
%setup -q -n desktop-defaults-ludora-%{version}

%build
# Nothing to build

%install
# fastfetch profile.d snippet (replaces bashrc append — works for all shells)
install -Dm644 ludora-fastfetch.sh \
    %{buildroot}%{_sysconfdir}/profile.d/ludora-fastfetch.sh

# Theme application scripts
install -Dm755 ludora-apply-theme.sh \
    %{buildroot}%{_bindir}/ludora-apply-theme.sh
install -Dm755 apply-ludora-theme-to-users.sh \
    %{buildroot}/usr/local/bin/apply-ludora-theme-to-users.sh

%post
# Live ISO files that the installer copied to installed systems before
# calamares-config-ludora 1.8-34. Each is removed only if it is still the
# exact file the ISO wrote, and never on the live session itself (it needs
# them). 49-nopasswd-wheel.rules gave wheel every polkit action without a
# password (pkexec = root); kscreenlockerrc turned screen locking off for
# new users.
if ! grep -qw rd.live.image /proc/cmdline 2>/dev/null && [ ! -x /usr/bin/calamares ]; then
    f=/etc/polkit-1/rules.d/49-nopasswd-wheel.rules
    [ -f $f ] && [ "$(sha256sum < $f | cut -d' ' -f1)" = 084e230e640c14eae8351fe7d52adcc890644b42a65edb9bbe48625daee196c2 ] && rm -f $f
    f=/etc/skel/.config/kscreenlockerrc
    [ -f $f ] && [ "$(sha256sum < $f | cut -d' ' -f1)" = efc39c3791bcfa5ba7a1aeaa6843bc3320c81dc1b80d71bfc0b36e2a3f0dee4d ] && rm -f $f
    for f in /etc/skel/.config/autostart/calamares-launcher.desktop /etc/skel/Desktop/install-ludora.desktop; do
        grep -qsx 'Exec=/usr/local/bin/calamares-launcher' $f && rm -f $f
    done
    rmdir /etc/skel/Desktop 2>/dev/null
    f=/usr/local/bin/calamares-launcher
    grep -qs '/usr/bin/calamares' $f && rm -f $f
    [ -d /etc/calamares ] && [ ! -e /etc/calamares/settings.conf ] && rm -rf /etc/calamares
fi
:

%files
%{_sysconfdir}/profile.d/ludora-fastfetch.sh
%{_bindir}/ludora-apply-theme.sh
/usr/local/bin/apply-ludora-theme-to-users.sh

%changelog
* Thu Nov 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-7
- Require ludora-leave, so every Ludora system has the way back to plain
  Fedora KDE

* Wed Nov 11 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-6
- Remove live ISO files that the installer left on installed systems
  (fixed for new installs in calamares-config-ludora 1.8-34): the
  passwordless polkit rule for wheel (pkexec = root without a password),
  skel's kscreenlockerrc (screen locking off for new users), the installer
  launcher and /etc/calamares. Only exact ISO copies are removed, and
  nothing on the live session

* Tue Nov 10 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-5
- Obsolete plasma-discover-offline-updates so Discover installs updates
  online by default. Offline updates (install on restart) got no snapper
  snapshot (45.1 VM test: 21 packages incl. kernel, no pre/post pair);
  online PackageKit transactions get one from libdnf5-plugin-snapper

* Sun Nov 01 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-4
- ludora-apply-theme.sh: broadcast KGlobalSettings notifyChange (palette)
  after applying the theme. When plasmashell had already loaded the light
  default palette, the panel stayed light until the next login (Ludora 45
  beta11; verified that the signal turns it dark without a restart)

* Sun Nov 01 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-3
- ludora-apply-theme.sh: drop the plasmashell restart from 1.1-2. Plasma
  6.8.2's plasmashell hangs on shutdown (WaylandClipboard thread join), so
  systemd aborted it after the stop timeout: ~40 s black screen and a crash
  report on first login (Ludora 45 beta10). Empty-panel cleanup stays

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-2
- ludora-apply-theme.sh: restart plasmashell once after applying the theme.
  Applied while plasmashell was still starting, the panel kept the light
  Breeze style until the next login (Ludora 45 beta9)

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-1
- ludora-apply-theme.sh: remove empty panels for 30 s after applying the
  theme. On first login plasmashell could still be creating its default
  layout, leaving an empty, screenless panel ("+ Add Widgets..." strip)
  next to the Ludora panel (Ludora 45 beta8)

