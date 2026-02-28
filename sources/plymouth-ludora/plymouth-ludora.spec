Name:       plymouth-ludora
Version:    1.0
Release:    2%{?dist}
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
# Only regenerate initramfs if we're not in an installation environment
# During anaconda installation, dracut will be called later by the kickstart
if [ "$1" -eq 1 ] && [ -x /usr/bin/dracut ] && [ ! -f /run/anaconda.pid ]; then
    # Check if we have a running kernel to regenerate for
    KERNEL_VER=$(uname -r 2>/dev/null)
    if [ -n "$KERNEL_VER" ] && [ -d "/lib/modules/$KERNEL_VER" ]; then
        dracut -f --quiet || true
    fi
fi
%files
%{_datadir}/plymouth/themes/spinner/watermark.png
%changelog
* Fri Feb 28 2025 Ludora Team <ludora@example.com> - 1.0-2
- Make dracut regeneration conditional to avoid anaconda installation failures
- Only run dracut on initial install, not during system installation
- Check for anaconda environment before running dracut
