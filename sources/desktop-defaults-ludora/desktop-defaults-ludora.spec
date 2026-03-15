Name:           desktop-defaults-ludora
Version:        1.1
Release:        0%{?dist}
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
