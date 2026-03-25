Name:           limine-snapper-sync
Version:        1.24.0
Release:        1%{?dist}
Summary:        Synchronize Limine bootloader entries with Snapper Btrfs snapshots

License:        GPL-3.0-or-later
URL:            https://gitlab.com/Zesko/limine-snapper-sync
Source0:        https://gitlab.com/Zesko/limine-snapper-sync/-/archive/%{version}/limine-snapper-sync-%{version}.tar.gz

BuildRequires:  gradle
BuildRequires:  java-21-openjdk-devel
BuildRequires:  systemd-rpm-macros
# Gradle downloads Maven dependencies at build time; network must be enabled in COPR
# (Project settings → Enable internet access during builds)

Requires:       java-21-openjdk-headless
Requires:       bash
Requires:       snapper
Requires:       btrfs-progs
Requires:       libnotify
Recommends:     inotify-tools

# Arch-specific package manager hooks are intentionally NOT included

%description
limine-snapper-sync automatically synchronizes Limine bootloader menu entries
with Btrfs snapshots managed by Snapper.

%prep
%autosetup -n limine-snapper-sync-%{version}

%build
# Build using the Gradle wrapper (requires network; enable in COPR project settings)
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
gradle --no-daemon --no-watch-fs installDist

%install
# --- JVM launcher (replaces the GraalVM native binary) ---
install -dm 0755 %{buildroot}/usr/lib/limine/jlib
cp build/install/limine-snapper-sync/lib/*.jar \
    %{buildroot}/usr/lib/limine/jlib/

cat > %{buildroot}/usr/lib/limine/limine-snapper-sync << 'LAUNCHER'
#!/bin/bash
exec java -cp '/usr/lib/limine/jlib/*' org.limine.snapper.Main "$@"
LAUNCHER
chmod 0755 %{buildroot}/usr/lib/limine/limine-snapper-sync

# --- Shell wrapper scripts ---
install -dm 0755 %{buildroot}%{_bindir}
for f in install/arch-linux/usr/bin/*; do
    install -m 0755 "$f" %{buildroot}%{_bindir}/
done

# --- limine-mutex helper ---
install -dm 0755 %{buildroot}/usr/lib/limine
install -m 0755 install/arch-linux/usr/lib/limine/limine-mutex \
    %{buildroot}/usr/lib/limine/limine-mutex

# --- Snapper plugin (same path on Fedora) ---
install -dm 0755 %{buildroot}/usr/lib/snapper/plugins
install -m 0755 \
    "install/arch-linux/usr/lib/snapper/plugins/10-limine-snapper-sync" \
    %{buildroot}/usr/lib/snapper/plugins/

# --- Systemd units ---
install -dm 0755 %{buildroot}%{_unitdir}
install -m 0644 \
    install/arch-linux/usr/lib/systemd/system/limine-snapper-sync.service \
    %{buildroot}%{_unitdir}/
install -dm 0755 %{buildroot}%{_unitdir}/snapper-cleanup.service.d
install -m 0644 \
    install/arch-linux/usr/lib/systemd/system/snapper-cleanup.service.d/limine-snapper-override.conf \
    %{buildroot}%{_unitdir}/snapper-cleanup.service.d/

# --- Config file ---
install -dm 0755 %{buildroot}%{_sysconfdir}
install -m 0644 install/arch-linux/etc/limine-snapper-sync.conf \
    %{buildroot}%{_sysconfdir}/limine-snapper-sync.conf

# --- XDG autostart desktop entries ---
install -dm 0755 %{buildroot}%{_sysconfdir}/xdg/autostart
install -m 0644 \
    install/arch-linux/etc/xdg/autostart/limine-restore-notify.desktop \
    %{buildroot}%{_sysconfdir}/xdg/autostart/
install -m 0644 \
    install/arch-linux/etc/xdg/autostart/limine-snapper-notify.desktop \
    %{buildroot}%{_sysconfdir}/xdg/autostart/

# --- Application desktop entry and icon ---
install -dm 0755 %{buildroot}%{_datadir}/applications
install -m 0644 \
    install/arch-linux/usr/share/applications/limine-snapper-restore.desktop \
    %{buildroot}%{_datadir}/applications/
install -dm 0755 \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
install -m 0644 \
    install/arch-linux/usr/share/icons/hicolor/128x128/apps/LimineSnapperSync.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/

%post
%systemd_post limine-snapper-sync.service

%preun
%systemd_preun limine-snapper-sync.service

%postun
%systemd_postun_with_restart limine-snapper-sync.service

%files
%license LICENSE
%doc README.md CHANGELOG.md
/usr/lib/limine/limine-snapper-sync
/usr/lib/limine/limine-mutex
/usr/lib/limine/jlib/
%{_bindir}/limine-snapper-info
%{_bindir}/limine-snapper-list
%{_bindir}/limine-snapper-notify
%{_bindir}/limine-snapper-remove
%{_bindir}/limine-snapper-restore
%{_bindir}/limine-snapper-sync
%{_bindir}/limine-snapper-watcher
/usr/lib/snapper/plugins/10-limine-snapper-sync
%{_unitdir}/limine-snapper-sync.service
%{_unitdir}/snapper-cleanup.service.d/limine-snapper-override.conf
%config(noreplace) %{_sysconfdir}/limine-snapper-sync.conf
%{_sysconfdir}/xdg/autostart/limine-restore-notify.desktop
%{_sysconfdir}/xdg/autostart/limine-snapper-notify.desktop
%{_datadir}/applications/limine-snapper-restore.desktop
%{_datadir}/icons/hicolor/128x128/apps/LimineSnapperSync.png

%changelog
* Wed Mar 25 2026 Your Name <your@email.com> - 1.24.0-1
- Initial packaging for Fedora/COPR
