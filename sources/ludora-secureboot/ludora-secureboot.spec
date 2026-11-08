Name:           ludora-secureboot
Version:        1.0
Release:        3%{?dist}
Summary:        Per-machine Secure Boot signing for Ludora kernels
License:        GPL-3.0-or-later
URL:            https://github.com/LarsSoeMikkelsen/Ludora
BuildArch:      noarch

Source0:        ludora-secureboot
Source1:        99-ludora-sign.install
Source2:        60-ludora-title.install

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

Boot entries are titled "Ludora 45 (...)", and Fedora's kernel, kept as
the signed fallback, "Ludora 45 with Fedora kernel (...)".

Nothing happens until 'ludora-secureboot setup' is run (the Ludora
installer does this when Secure Boot is enabled).

%prep

%build

%install
install -Dm0755 %{SOURCE0} %{buildroot}%{_sbindir}/ludora-secureboot
install -Dm0755 %{SOURCE1} %{buildroot}%{_prefix}/lib/kernel/install.d/99-ludora-sign.install
install -Dm0755 %{SOURCE2} %{buildroot}%{_prefix}/lib/kernel/install.d/60-ludora-title.install

# Retitle entries of kernels installed before this package
%posttrans
for d in /lib/modules/*; do
    [ -d "$d" ] && %{_prefix}/lib/kernel/install.d/60-ludora-title.install add "${d##*/}" || :
done

# akmods installed after setup: give it the Ludora key before it generates
# its own on first use
%triggerin -- akmods
[ -e /etc/pki/ludora-secureboot/MOK.key ] && %{_sbindir}/ludora-secureboot akmods-key || :

%files
%{_sbindir}/ludora-secureboot
%{_prefix}/lib/kernel/install.d/99-ludora-sign.install
%{_prefix}/lib/kernel/install.d/60-ludora-title.install

%changelog
* Sat Nov 07 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-3
- setup: rebuild akmod modules (akmods --rebuild) when the Ludora key
  replaces a key akmods already had; modules signed with the old,
  unenrolled key would not load with Secure Boot on. Skipped in the
  installer chroot and in the akmods RPM trigger
- fix_boot_entry: check every step. It runs under '|| warn', where set -e
  is off, so a failed grub2-probe used to write a grub.cfg stub with an
  empty UUID and still replace the boot entry. Nothing is written now until
  all inputs are known, and the new entry is verified afterwards
- kernel-install hook 60-ludora-title.install: GRUB entries read
  "Ludora 45 (<kernel>)", "Ludora 45 with Fedora kernel (<kernel>)" and
  "Ludora 45 rescue" instead of "Fedora Linux (<kernel>) 45 (Forty Five)";
  existing entries are retitled on update

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-2
- Name the key after /etc/hostname: in the installer `hostname` still
  reported the live system, giving keys called "(localhost-live)"

* Sat Oct 31 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-1
- Initial package of the ludora-secureboot prototype
- kernel-install hook shipped in /usr/lib/kernel/install.d (no-op without a key)
- setup: --password-stdin for the installer, Ludora key doubles as the akmods
  key, moves the "Ludora" boot entry from the unsigned \EFI\Ludora GRUB to
  Fedora's signed shim
- status: shows boot entry and akmods key state
