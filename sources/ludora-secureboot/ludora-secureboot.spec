Name:           ludora-secureboot
Version:        1.0
Release:        1%{?dist}
Summary:        Per-machine Secure Boot signing for Ludora kernels
License:        GPL-3.0-or-later
URL:            https://github.com/LarsSoeMikkelsen/Ludora
BuildArch:      noarch

Source0:        ludora-secureboot
Source1:        99-ludora-sign.install

Requires:       sbsigntools
Requires:       mokutil
Requires:       openssl
Requires:       efibootmgr
Requires:       grub2-tools
Requires:       util-linux

%description
Creates a per-machine Machine Owner Key (MOK), enrolls it with shim's
MokManager, and signs every installed and future kernel image with it, so
Ludora kernels boot with UEFI Secure Boot enabled. The key is also used as
the akmods signing key, so akmod modules (e.g. NVIDIA) load under Secure
Boot with the same enrollment. Setup also points the "Ludora" boot entry
at Fedora's signed shim on installs made before that was the default.

Nothing happens until 'ludora-secureboot setup' is run (the Ludora
installer does this when Secure Boot is enabled).

%prep

%build

%install
install -Dm0755 %{SOURCE0} %{buildroot}%{_sbindir}/ludora-secureboot
install -Dm0755 %{SOURCE1} %{buildroot}%{_prefix}/lib/kernel/install.d/99-ludora-sign.install

# akmods installed after setup: give it the Ludora key before it generates
# its own on first use
%triggerin -- akmods
[ -e /etc/pki/ludora-secureboot/MOK.key ] && %{_sbindir}/ludora-secureboot akmods-key || :

%files
%{_sbindir}/ludora-secureboot
%{_prefix}/lib/kernel/install.d/99-ludora-sign.install

%changelog
* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-1
- Initial package of the ludora-secureboot prototype
- kernel-install hook shipped in /usr/lib/kernel/install.d (no-op without a key)
- setup: --password-stdin for the installer, Ludora key doubles as the akmods
  key, moves the "Ludora" boot entry from the unsigned \EFI\Ludora GRUB to
  Fedora's signed shim
- status: shows boot entry and akmods key state
