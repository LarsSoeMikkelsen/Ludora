Name:           ludora-game-mode
Version:        0.1
Release:        3%{?dist}
Summary:        Switch between the Plasma desktop and Steam Big Picture (Game Mode)
License:        GPL-3.0-or-later
URL:            https://github.com/LarsSoeMikkelsen/Ludora
BuildArch:      noarch

Source0:        ludora-game-mode
Source1:        set-session
Source2:        os-session-select
Source3:        org.ludora.game-mode.policy
Source4:        ludora-game-mode.desktop
Source5:        ludora-game-mode-session.desktop
Source6:        relogin

Requires:       gamescope-session-steam
Requires:       plasma-login-manager
Requires:       polkit
Requires:       kdialog
Requires:       xdg-user-dirs
Requires:       util-linux
Requires:       systemd

%description
Game Mode for Ludora: a "Game Mode" icon on the desktop (and in the
application menu) logs out of Plasma straight into Steam Big Picture running
full screen in gamescope; Steam's Power -> Switch to Desktop goes back.
The switch uses Plasma Login Manager's autologin, kept in /run, so a reboot
always returns to the normal login. Not available while booted into a
snapshot.

%prep

%build

%install
install -Dm0755 %{SOURCE0} %{buildroot}%{_bindir}/ludora-game-mode
install -Dm0755 %{SOURCE1} %{buildroot}%{_libexecdir}/ludora-game-mode/set-session
install -Dm0755 %{SOURCE6} %{buildroot}%{_libexecdir}/ludora-game-mode/relogin
install -Dm0755 %{SOURCE2} %{buildroot}%{_prefix}/lib/os-session-select
install -Dm0644 %{SOURCE3} %{buildroot}%{_datadir}/polkit-1/actions/org.ludora.game-mode.policy
install -Dm0644 %{SOURCE4} %{buildroot}%{_datadir}/applications/ludora-game-mode.desktop
install -Dm0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/xdg/autostart/ludora-game-mode-session.desktop
install -d %{buildroot}%{_sysconfdir}/plasmalogin.conf.d
ln -s /run/ludora/game-mode.conf %{buildroot}%{_sysconfdir}/plasmalogin.conf.d/60-ludora-game-mode.conf

%files
%{_bindir}/ludora-game-mode
%dir %{_libexecdir}/ludora-game-mode
%{_libexecdir}/ludora-game-mode/set-session
%{_libexecdir}/ludora-game-mode/relogin
%{_prefix}/lib/os-session-select
%{_datadir}/polkit-1/actions/org.ludora.game-mode.policy
%{_datadir}/applications/ludora-game-mode.desktop
%{_sysconfdir}/xdg/autostart/ludora-game-mode-session.desktop
%{_sysconfdir}/plasmalogin.conf.d/60-ludora-game-mode.conf

%changelog
* Sat Nov 14 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 0.1-3
- Restart Plasma Login Manager once the session has ended: it only applies
  an autologin it loaded at start, so the switch never happened (VM test)

* Sat Nov 14 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 0.1-2
- Label /run/ludora/game-mode.conf xdm_var_run_t: SELinux kept Plasma Login
  Manager from reading it, so the Game Mode autologin was ignored (VM test)

* Fri Nov 13 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 0.1-1
- Prototype (ludora-dev): Game Mode desktop icon and menu entry, Steam
  "Switch to Desktop" hook, root helper limited to the caller's autologin
