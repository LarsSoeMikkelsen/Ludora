Name:           ludora-leave
Version:        1.0
Release:        1%{?dist}
Summary:        Turn a Ludora install back into plain Fedora KDE
License:        GPL-3.0-or-later
URL:            https://github.com/LarsSoeMikkelsen/Ludora
BuildArch:      noarch

Source0:        ludora-leave
Source1:        ludora-leave.desktop

Requires:       python3
Requires:       dnf5
Requires:       grubby
Requires:       grub2-tools
Requires:       polkit
Requires:       util-linux
Requires:       rpm

%description
ludora-leave switches a Ludora system back to plain Fedora KDE without a
reinstall: it takes a snapshot, removes the Ludora COPR, makes Fedora's
kernel the default, removes the Ludora-only packages, replaces Ludora's
builds of Fedora packages with Fedora's (dnf distro-sync), and restores
Fedora's boot menu names, boot splash and firmware boot entry. It can also
delete the Ludora Secure Boot key. It needs only Fedora's repositories, so
it keeps working if the Ludora repository is gone, and removes itself last.

Run it from the menu (Leave Ludora), the welcome app, or with
'sudo ludora-leave'; 'ludora-leave --dry-run' shows the plan.

%prep

%build

%install
install -Dm0755 %{SOURCE0} %{buildroot}%{_bindir}/ludora-leave
install -Dm0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/ludora-leave.desktop

%files
%{_bindir}/ludora-leave
%{_datadir}/applications/ludora-leave.desktop

%changelog
* Thu Nov 12 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-1
- Initial package
