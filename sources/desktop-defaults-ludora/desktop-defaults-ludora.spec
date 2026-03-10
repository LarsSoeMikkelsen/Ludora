Name:           desktop-defaults-ludora
Version:        1.0
Release:        1%{?dist}
Summary:        KDE desktop defaults and system configuration for Ludora Gaming Edition
License:        GPLv3+
URL:            https://ludora.org
Source0:        desktop-defaults-ludora-%{version}.tar.gz
BuildArch:      noarch
Requires:       kde-ludora
Requires:       fastfetch
Requires:       polkit

%description
System-wide desktop defaults for Ludora Gaming Edition.
Provides:
  - KDE Plasma global theme defaults (kdeglobals, plasmashellrc)
  - Polkit rule granting wheel group passwordless access
  - fastfetch display on interactive shell startup (via profile.d)
  - Theme application scripts for new users on first login

%define debug_package %{nil}

%prep
%setup -q -n desktop-defaults-ludora-%{version}

%build
# Nothing to build

%install
# KDE system-wide defaults
install -Dm644 kdeglobals \
    %{buildroot}%{_sysconfdir}/xdg/kdeglobals
install -Dm644 plasmashellrc \
    %{buildroot}%{_sysconfdir}/xdg/plasmashellrc

# Polkit wheel rule
install -Dm644 49-nopasswd-wheel.rules \
    %{buildroot}%{_sysconfdir}/polkit-1/rules.d/49-nopasswd-wheel.rules

# fastfetch profile.d snippet (replaces bashrc append — works for all shells)
install -Dm644 ludora-fastfetch.sh \
    %{buildroot}%{_sysconfdir}/profile.d/ludora-fastfetch.sh

# Theme application scripts
install -Dm755 ludora-apply-theme.sh \
    %{buildroot}%{_bindir}/ludora-apply-theme.sh
install -Dm755 apply-ludora-theme-to-users.sh \
    %{buildroot}/usr/local/bin/apply-ludora-theme-to-users.sh

%files
%{_sysconfdir}/xdg/kdeglobals
%{_sysconfdir}/xdg/plasmashellrc
%{_sysconfdir}/polkit-1/rules.d/49-nopasswd-wheel.rules
%{_sysconfdir}/profile.d/ludora-fastfetch.sh
%{_bindir}/ludora-apply-theme.sh
/usr/local/bin/apply-ludora-theme-to-users.sh

%changelog
* Tue Mar 10 2026 Ludora Team <team@ludora.org> - 1.0-1
- Initial release
