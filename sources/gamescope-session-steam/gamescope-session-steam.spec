%global commit      1a3fdb7fa15a4bba7204bef69702b7a10a297828
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate  20241205

Name:           gamescope-session-steam
Version:        0^%{commitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Steam Big Picture session for gamescope-session-plus
License:        MIT
URL:            https://github.com/ChimeraOS/gamescope-session-steam
# Upstream has no releases; pinned commit
Source0:        %{url}/archive/%{commit}/gamescope-session-steam-%{shortcommit}.tar.gz
BuildArch:      noarch

Requires:       gamescope-session-plus
Requires:       steam

%description
Runs Steam in Big Picture (SteamOS gamepad UI) mode inside gamescope as a
login session, plus the steamos-* helper commands the Steam client calls.

Ludora: the upstream polkit policy is not shipped. It let any user, even a
remote one, run the update helpers as root without a password; on Ludora they
do nothing (ChimeraOS's frzr updater is not installed), so the helpers run
unprivileged instead.

%prep
%autosetup -n gamescope-session-steam-%{commit}

%build

%install
cp -a usr %{buildroot}/
rm -f %{buildroot}%{_datadir}/polkit-1/actions/org.chimeraos.update.policy
rmdir -p --ignore-fail-on-non-empty %{buildroot}%{_datadir}/polkit-1/actions
# Unprivileged helpers: Steam calls these paths; without frzr they only
# report "no update" / "no branches".
for h in steamos-update steamos-select-branch jupiter-biosupdate; do
    printf '#!/bin/bash\nexec /usr/bin/%s "$@"\n' "$h" \
        > %{buildroot}%{_bindir}/steamos-polkit-helpers/$h
    chmod 0755 %{buildroot}%{_bindir}/steamos-polkit-helpers/$h
done
# Both upstream session files are named "Steam Big Picture"; keep one
rm -f %{buildroot}%{_datadir}/wayland-sessions/gamescope-session.desktop

%files
%license LICENSE
%{_bindir}/jupiter-biosupdate
%{_bindir}/steam-http-loader
%{_bindir}/steamos-select-branch
%{_bindir}/steamos-session-select
%{_bindir}/steamos-update
%dir %{_bindir}/steamos-polkit-helpers
%{_bindir}/steamos-polkit-helpers/jupiter-biosupdate
%{_bindir}/steamos-polkit-helpers/steamos-select-branch
%{_bindir}/steamos-polkit-helpers/steamos-update
%{_datadir}/applications/gamescope-mimeapps.list
%{_datadir}/applications/steam_http_loader.desktop
%{_datadir}/gamescope-session-plus/sessions.d/
%{_datadir}/wayland-sessions/gamescope-session-steam.desktop

%changelog
* Fri Nov 13 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 0^20241205git1a3fdb7-1
- Initial package for Ludora Game Mode (ludora-dev prototype); no polkit
  policy, unprivileged steamos-polkit-helpers
