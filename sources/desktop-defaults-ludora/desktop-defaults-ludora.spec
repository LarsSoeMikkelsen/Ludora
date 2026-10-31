Name:           desktop-defaults-ludora
Version:        1.1
Release:        2%{?dist}
Summary:        KDE desktop defaults and system configuration for Ludora
License:        GPLv3+
URL:            https://ludora.org
Source0:        desktop-defaults-ludora-%{version}.tar.gz
BuildArch:      noarch
Requires:       kde-ludora
Requires:       fastfetch
Requires:       polkit

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

%files
%{_sysconfdir}/profile.d/ludora-fastfetch.sh
%{_bindir}/ludora-apply-theme.sh
/usr/local/bin/apply-ludora-theme-to-users.sh

%changelog
* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-2
- ludora-apply-theme.sh: restart plasmashell once after applying the theme.
  Applied while plasmashell was still starting, the panel kept the light
  Breeze style until the next login (Ludora 45 beta9)

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.1-1
- ludora-apply-theme.sh: remove empty panels for 30 s after applying the
  theme. On first login plasmashell could still be creating its default
  layout, leaving an empty, screenless panel ("+ Add Widgets..." strip)
  next to the Ludora panel (Ludora 45 beta8)

