Name:           ludora-secureboot
Version:        1.0
Release:        7%{?dist}
Summary:        Per-machine Secure Boot signing for Ludora kernels
License:        GPL-3.0-or-later
URL:            https://github.com/LarsSoeMikkelsen/Ludora
BuildArch:      noarch

Source0:        ludora-secureboot
Source1:        99-ludora-sign.install
Source2:        60-ludora-title.install
Source3:        65-ludora-fallback.install

Requires:       sbsigntools
Requires:       mokutil
Requires:       openssl
Requires:       efibootmgr
Requires:       grub2-tools
Requires:       util-linux
Requires:       grubby
# Fedora's kernel is the signed fallback: it boots with Secure Boot on when a
# Ludora kernel is refused (key not enrolled, signing failed, key reverted).
# kernel-ludora-core provides plain "kernel" too, but only Fedora's kernel
# package provides the arch-tagged kernel(x86-64), so this pulls it in.
# Installs from Ludora 45.0 had it removed by the installer.
Requires:       kernel(x86-64)

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
install -Dm0755 %{SOURCE3} %{buildroot}%{_prefix}/lib/kernel/install.d/65-ludora-fallback.install

# Retitle entries of kernels installed before this package
%posttrans
for d in /lib/modules/*; do
    [ -d "$d" ] && %{_prefix}/lib/kernel/install.d/60-ludora-title.install add "${d##*/}" || :
done
# Default = newest Ludora kernel, fallback = Fedora's kernel on existing installs
%{_prefix}/lib/kernel/install.d/65-ludora-fallback.install add || :

# akmods installed after setup: give it the Ludora key before it generates
# its own on first use
%triggerin -- akmods
[ -e /etc/pki/ludora-secureboot/MOK.key ] && %{_sbindir}/ludora-secureboot akmods-key || :

%triggerin -- kernel-ludora-core
# Keep kernel-ludora the GRUB default while it is installed. 20-grub.install
# takes the default kernel type from DEFAULTKERNEL, so without this every
# Fedora kernel update would become the default; 65-ludora-fallback.install
# also only repairs saved_entry while DEFAULTKERNEL=kernel-ludora-core.
# Runs before Fedora's kernel runs kernel-install (%%posttrans) when both
# arrive in one transaction.
# A DEFAULTKERNEL the user set to anything else is left alone.
f=/etc/sysconfig/kernel
if [ ! -f $f ] || ! grep -q '^DEFAULTKERNEL=' $f; then
    echo 'DEFAULTKERNEL=kernel-ludora-core' >> $f
elif grep -qx 'DEFAULTKERNEL=kernel-core' $f; then
    sed -i 's/^DEFAULTKERNEL=kernel-core$/DEFAULTKERNEL=kernel-ludora-core/' $f
fi
:

%triggerpostun -- kernel-ludora-core
# Last Ludora kernel removed: Fedora's kernel is the default again
if [ "$2" -eq 0 ] && [ -f /etc/sysconfig/kernel ]; then
    sed -i 's/^DEFAULTKERNEL=kernel-ludora-core$/DEFAULTKERNEL=kernel-core/' /etc/sysconfig/kernel
fi
:

%files
%{_sbindir}/ludora-secureboot
%{_prefix}/lib/kernel/install.d/99-ludora-sign.install
%{_prefix}/lib/kernel/install.d/60-ludora-title.install
%{_prefix}/lib/kernel/install.d/65-ludora-fallback.install

%changelog
* Wed Nov 11 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-7
- Correct the 1.0-6 notes: Fedora's 20-grub.install does honour
  DEFAULTKERNEL (only Ludora kernel installs move the default). The
  65-ludora-fallback.install change repairs a saved_entry that is unset or
  points at a removed kernel, which made GRUB boot Fedora's kernel

* Wed Nov 11 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-6
- 65-ludora-fallback.install also sets GRUB's default (saved_entry) to the
  newest Ludora kernel on every kernel add/remove, while
  DEFAULTKERNEL=kernel-ludora-core. Fedora's hooks never moved the default,
  so GRUB booted the highest-sorting entry: Fedora's kernel when both have
  the same upstream version (7.3.3-300.fc45 > 7.3.3-100.ludora)

* Sun Nov 08 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-5
- kernel-install hook 65-ludora-fallback.install: GRUB's fallback entry is
  the newest Fedora kernel, so a Ludora kernel refused under Secure Boot
  boots Fedora's kernel instead of stopping at the menu

* Sun Nov 08 2026 Lars Søe Mikkelsen <larssoemikkelsen@gmail.com> - 1.0-4
- Require Fedora's kernel (kernel(x86-64)) as the signed fallback; installs
  from Ludora 45.0 had it removed by the installer
- Keep DEFAULTKERNEL=kernel-ludora-core while kernel-ludora is installed,
  so Fedora kernel updates do not become the GRUB default; back to
  kernel-core when the last Ludora kernel is removed
- revert: with Secure Boot on, refuse unless --force (Ludora kernels would
  be refused at boot); --force makes Fedora's kernel the default first
- Boot entry repair creates the new entry before deleting the old one
- status: vendor-signed kernels could be shown as UNSIGNED (pipefail)

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
