%global commit      73d2da84ace7f41006a0f85bd2fdb19ef593a464
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate  20260106

Name:           gamescope-session-plus
Version:        0^%{commitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Generic gamescope session runner (Steam Big Picture style sessions)
License:        MIT
URL:            https://github.com/ChimeraOS/gamescope-session
# Upstream has no releases; pinned commit
Source0:        %{url}/archive/%{commit}/gamescope-session-%{shortcommit}.tar.gz
BuildArch:      noarch

Requires:       gamescope
Requires:       bash
Requires:       dbus-tools
Requires:       pciutils
Recommends:     mangohud

%description
gamescope-session-plus starts a full-screen gamescope compositor with a
client (for example Steam in Big Picture mode) as a login session, with the
environment SteamOS uses. Clients are described in
/usr/share/gamescope-session-plus/sessions.d.

%prep
%autosetup -n gamescope-session-%{commit}

%build

%install
cp -a usr %{buildroot}/

%files
%license LICENSE
%doc README.md
%{_bindir}/export-gpu
%{_bindir}/gamescope-session-plus
%{_userunitdir}/gamescope-session-plus@.service
%dir %{_datadir}/gamescope-session-plus
%{_datadir}/gamescope-session-plus/device-quirks
%{_datadir}/gamescope-session-plus/gamescope-session-plus
%dir %{_datadir}/gamescope
%dir %{_datadir}/gamescope/scripts
%dir %{_datadir}/gamescope/scripts/50-custom
%{_datadir}/gamescope/scripts/50-custom/50-disable-explicit-sync.lua

%changelog
* Fri Nov 13 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 0^20260106git73d2da8-1
- Initial package for Ludora Game Mode (ludora-dev prototype)
