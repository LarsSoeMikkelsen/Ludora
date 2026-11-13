Name:           ludora-leave
Version:        1.0
Release:        7%{?dist}
Summary:        Turn a Ludora install back into plain Fedora KDE
License:        GPL-3.0-or-later
URL:            https://github.com/LarsSoeMikkelsen/Ludora
BuildArch:      noarch

Source0:        ludora-leave
Source1:        ludora-leave.desktop
Source2:        ludora-leave-reminder.desktop
Source3:        ludora_leave_gui.py
Source4:        org.ludora.leave.policy

Requires:       python3
# the window (ludora-leave as the user)
Requires:       python3-pyqt6
Requires:       dnf5
Requires:       grubby
Requires:       grub2-tools
Requires:       polkit
Requires:       util-linux
Requires:       rpm
# notify-send for the reminder
Requires:       libnotify

%description
ludora-leave switches a Ludora system back to plain Fedora KDE without a
reinstall: it takes a snapshot, removes the Ludora COPR, makes Fedora's
kernel the default, removes the Ludora-only packages, replaces Ludora's
builds of Fedora packages with Fedora's (dnf distro-sync), and restores
Fedora's boot menu names, boot splash and firmware boot entry. It can also
delete the Ludora Secure Boot key. It needs only Fedora's repositories, so
it keeps working if the Ludora repository is gone, and removes itself last.

Run it from the menu (Leave Ludora) or the welcome app: a window shows
what will happen and asks for the password only when you press Leave
Ludora. 'sudo ludora-leave' does the same in a terminal;
'ludora-leave --dry-run' shows the plan.

At login it checks whether the Ludora kernel has been behind Fedora's
kernel for 60 days (a sign that Ludora is no longer maintained) and then
shows a reminder with a button to leave, at most once a week.

%prep

%build

%install
install -Dm0755 %{SOURCE0} %{buildroot}%{_bindir}/ludora-leave
install -Dm0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/ludora-leave.desktop
install -Dm0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/xdg/autostart/ludora-leave-reminder.desktop
install -Dm0644 %{SOURCE3} %{buildroot}%{_datadir}/ludora-leave/ludora_leave_gui.py
install -Dm0644 %{SOURCE4} %{buildroot}%{_datadir}/polkit-1/actions/org.ludora.leave.policy

%files
%{_bindir}/ludora-leave
%{_datadir}/applications/ludora-leave.desktop
%{_sysconfdir}/xdg/autostart/ludora-leave-reminder.desktop
%{_datadir}/ludora-leave/
%{_datadir}/polkit-1/actions/org.ludora.leave.policy

%changelog
* Fri Nov 13 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-7
- A window (as the user) explains what will happen and shows the plan
  before anything asks for a password; the password is asked only when
  you press Leave Ludora, then the window shows the progress and offers
  a reboot. 'sudo ludora-leave' in a terminal works as before
- polkit action org.ludora.leave: the password dialog says what it is for
- The menu entry, the welcome app and the login reminder open the window

* Thu Nov 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-6
- Login reminder (autostart, --notify-if-stale): when Fedora's kernel has
  been a newer upstream version than every Ludora kernel for 60 days,
  notify that Ludora may no longer be maintained, with Leave Ludora and
  Don't remind me actions; at most once a week

* Thu Nov 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-5
- Plan: say when the Ludora repository is already removed

* Thu Nov 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-4
- Second run (after an interruption): do not pass --disable-repo for the
  COPR once its repo files are gone; dnf5 rejects a pattern that matches
  no repository

* Thu Nov 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-3
- When stopped by an error or Ctrl-C after the first step, say that the
  finished steps stay done and that running it again finishes the rest

* Thu Nov 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-2
- Boot splash: the spinner watermark belongs to fedora-logos; reinstall
  the file's owner instead of plymouth-theme-spinner

* Thu Nov 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-1
- Initial package
