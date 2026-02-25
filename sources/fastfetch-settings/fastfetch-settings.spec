Name:           fastfetch-settings
Version:        1.0
Release:        1%{?dist}
Summary:        Ludora fastfetch configuration and logo
License:        GPLv2+
URL:            https://github.com/LarsSoeMikkelsen/Ludora
Source0:        fastfetch-settings-%{version}.tar.gz
BuildArch:      noarch
Requires:       fastfetch
%description
Ludora-branded fastfetch configuration featuring the Ludora logo
and a curated set of system info modules.
%define debug_package %{nil}
%prep
%setup -T -b 0 -q -n fastfetch-settings-%{version}
%build
%install
mkdir -p %{buildroot}%{_datadir}/fastfetch/logos
mkdir -p %{buildroot}%{_sysconfdir}/fastfetch
cp ludora.txt %{buildroot}%{_datadir}/fastfetch/logos/ludora.txt
cp config.jsonc %{buildroot}%{_sysconfdir}/fastfetch/config.jsonc
%files
%{_datadir}/fastfetch/logos/ludora.txt
%{_sysconfdir}/fastfetch/config.jsonc
%changelog
* Mon Feb 24 2025 Ludora Team <team@ludora.org> - 1.0-1
- Initial Ludora fastfetch configuration
