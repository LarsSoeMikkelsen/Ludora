Name:       plymouth-ludora
Version:    1.0
Release:    1%{?dist}
Summary:    Ludora Plymouth watermark for the spinner theme
License:    GPL-3.0
BuildArch:  noarch
Requires:   plymouth-theme-spinner
Source0:    watermark.png

%description
Replaces the default Plymouth spinner theme watermark with the Ludora branding.

%install
install -Dm644 %{SOURCE0} %{buildroot}%{_datadir}/plymouth/themes/spinner/watermark.png

%post
if [ -x /usr/bin/dracut ]; then
    dracut -f --quiet || true
fi

%files
%{_datadir}/plymouth/themes/spinner/watermark.png
