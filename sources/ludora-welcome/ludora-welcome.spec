Name:           ludora-welcome
Version:        1.2
Release:        0%{?dist}
Summary:        First-boot welcome application for Ludora
License:        GPLv3+
URL:            https://ludora.org
Source0:        ludora-welcome-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3-pyqt6
Requires:       kde-ludora

%description
A simple welcome application that runs on first boot, introducing the user
to Ludora, explaining how to upgrade the system with dnf instead of KDE Discover,
and guiding NVIDIA driver installation using the pre-enabled RPM Fusion repositories.

%define debug_package %{nil}

%prep
%setup -q -n ludora-welcome-%{version}

%build
# Nothing to build

%install
install -Dm755 ludora-welcome.py \
    %{buildroot}%{_bindir}/ludora-welcome

install -Dm644 ludora-welcome.desktop \
    %{buildroot}%{_sysconfdir}/xdg/autostart/ludora-welcome.desktop

install -Dm644 ludora-welcome-app.desktop \
    %{buildroot}%{_datadir}/applications/ludora-welcome.desktop

%files
%{_bindir}/ludora-welcome
%{_sysconfdir}/xdg/autostart/ludora-welcome.desktop
%{_datadir}/applications/ludora-welcome.desktop

%changelog
* Wed May 13 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 1.2-0
- Welcome tab: expand optional section to list all five netinstall groups
- Upgrading tab: remove major Fedora version upgrade section

* Wed May 13 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-0
- Update Welcome tab: split included/optional components to reflect modular installer
- Update NVIDIA tab: add 580xx legacy branch for Maxwell/Pascal (GTX 9xx/10xx/16xx)
