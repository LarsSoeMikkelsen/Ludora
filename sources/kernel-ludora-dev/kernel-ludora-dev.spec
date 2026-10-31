# Fedora bits
%define __spec_install_post %{__os_install_post}
%define _build_id_links none
%define _default_patch_fuzz 2
%define _disable_source_fetch 0
%define debug_package %{nil}
%define make_build make %{?_lto_args} %{?_smp_mflags}
%undefine __brp_mangle_shebangs
%undefine _auto_set_build_flags
%undefine _include_frame_pointers

# Linux Kernel Versions
%define _basekver 7.2
%define _stablekver 11
%define _releasekver 3
%define _rpmver %{version}-%{release}
%define _kver %{_rpmver}.%{_arch}

# Define the tickrate used by the kernel
# Valid values: 100, 250, 300, 500, 600, 750 and 1000
%define _hz_tick 1000

# Defines the x86_64 ISA level used to compile the kernel
# Valid values are 1-4
%define _x86_64_lvl 3

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

%define _kernel_dir /lib/modules/%{_kver}
%define _devel_dir %{_usrsrc}/kernels/%{_kver}

Name:           kernel-ludora-dev
Summary:        Linux BORE kernel
Version:        %{_basekver}.%{_stablekver}
Release:        %{_releasekver}.ludora%{?dist}
License:        GPL-2.0-only
URL:            https://github.com/LarsSoeMikkelsen/Ludora

Requires:       kernel-core-uname-r = %{_kver}
Requires:       kernel-modules-uname-r = %{_kver}
Requires:       kernel-modules-core-uname-r = %{_kver}
Provides:       installonlypkg(kernel)

BuildRequires:  bc
BuildRequires:  bison
BuildRequires:  dwarves
BuildRequires:  elfutils-devel
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  gettext-devel
BuildRequires:  kmod
BuildRequires:  make
BuildRequires:  openssl
BuildRequires:  openssl-devel
BuildRequires:  perl-Carp
BuildRequires:  perl-devel
BuildRequires:  perl-generators
BuildRequires:  perl-interpreter
BuildRequires:  python3-devel
BuildRequires:  python3-pyyaml
BuildRequires:  python-srpm-macros

Source0:        https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-%{version}.tar.xz
Source1:        config

Patch0:         0001-bore.patch
Patch1:         0001-hid-usbhid-sanitize-uniq-against-control-chars.patch
Patch2:         0001-usb-core-truncate-string-descriptors-at-first-C0-con.patch
Patch3:         0001-cachyos-default-tunables.patch
# Piece-Of-Cake idle CPU selector, from CachyOS/linux 7.2/cachy
# (85777b42e511 + 5c28b6663fbb, both in cachyos-7.2.11-1); re-check each bump
Patch4:         0001-sched-poc-selector-v2.6.2.patch
Patch5:         0002-sched-poc-selector-v2.6.3.patch

%description
The meta package for %{name}.

%prep
%setup -q -n linux-%{version}
%autopatch -p1 -v -M 9

    cp %{SOURCE1} .config
    make olddefconfig

    scripts/config -e SCHED_BORE

    scripts/config --set-str CONFIG_LSM lockdown,yama,integrity,selinux,bpf,landlock

    scripts/config -u DEFAULT_HOSTNAME

    case %{_hz_tick} in
        100|250|300|500|600|750|1000)
            scripts/config -e HZ_%{_hz_tick} --set-val HZ %{_hz_tick};;
        *)
            echo "Invalid tickrate value, using default 1000"
            scripts/config -e HZ_1000 --set-val HZ 1000;;
    esac

    # Mainline has no X86_64_VERSION Kconfig (that is a CachyOS patch), so set
    # the ISA level directly where arch/x86/Makefile picks the generic -march
    %if %{_x86_64_lvl} < 5 && %{_x86_64_lvl} > 1
        _march=x86-64-v%{_x86_64_lvl}
    %elif %{_x86_64_lvl} == 1
        _march=x86-64
    %else
        echo "Invalid x86_64 ISA Level. Using x86_64_v3"
        _march=x86-64-v3
    %endif
    sed -i -e "s/-march=x86-64 -mtune=generic/-march=${_march} -mtune=generic/" \
           -e "s/-Ctarget-cpu=x86-64 -Ztune-cpu=generic/-Ctarget-cpu=${_march} -Ztune-cpu=generic/" \
           arch/x86/Makefile
    grep -q -- "-march=${_march} -mtune=generic" arch/x86/Makefile
    scripts/config -d X86_NATIVE_CPU

    # Gaming tuning
    # Full static preemption — lower latency than Fedora's PREEMPT_DYNAMIC/LAZY default
    scripts/config -d PREEMPT_NONE -d PREEMPT_VOLUNTARY -d PREEMPT_LAZY -d PREEMPT_DYNAMIC -e PREEMPT

    # BBR built-in and default — better latency under load than cubic
    # DEFAULT_TCP_CONG is derived from the DEFAULT_* choice, so select that
    scripts/config -e TCP_CONG_BBR -d DEFAULT_CUBIC -e DEFAULT_BBR --set-str DEFAULT_TCP_CONG bbr

    # FQ built-in — pairs with BBR for per-flow pacing
    scripts/config -e NET_SCH_FQ

    # LATENCYTOP adds per-task latency tracking overhead with no gaming benefit
    scripts/config -d LATENCYTOP

    # NUMA auto-balancing adds latency jitter on single-socket systems
    scripts/config -d NUMA_BALANCING_DEFAULT_ENABLED

    # THP always (CachyOS default) — games and Proton rarely madvise
    scripts/config -d TRANSPARENT_HUGEPAGE_MADVISE -e TRANSPARENT_HUGEPAGE_ALWAYS

    # Boost preempted RCU readers so they can't stall grace periods under load
    # RCU_BOOST is only visible with RCU_EXPERT
    scripts/config -e RCU_EXPERT -e RCU_BOOST

    # Compress modules at install time, after Kbuild signs them. Fedora's
    # config leaves them as plain .ko, and brp-strip then strips every ELF
    # file, dropping the appended signature; Secure Boot refuses the module
    scripts/config -d MODULE_COMPRESS_XZ -e MODULE_COMPRESS_ZSTD -e MODULE_COMPRESS_ALL

    # Drop Fedora's debug/hardening options that kernel-ludora (Cachy config)
    # also leaves off: UBSAN instruments every array access and shift,
    # DEBUG_LIST checks every list op (BUG_ON_DATA_CORRUPTION selects it;
    # LIST_HARDENED stays), and partitioned kmalloc caches plus no slab
    # merging spread allocations over more caches
    scripts/config -d UBSAN -d BUG_ON_DATA_CORRUPTION -d DEBUG_LIST \
                   -d KMALLOC_PARTITION_CACHES -e SLAB_MERGE_DEFAULT

    # Faster idle CPU search on wakeup (CachyOS POC selector, Patch4/5)
    scripts/config -e SCHED_POC_SELECTOR

    # Kconfig silently drops options whose dependencies aren't met, so check
    # that the tuning survived
    make olddefconfig
    for opt in SCHED_BORE HZ_1000 PREEMPT DEFAULT_BBR NET_SCH_FQ \
               TRANSPARENT_HUGEPAGE_ALWAYS RCU_BOOST \
               MODULE_SIG_ALL MODULE_COMPRESS_ZSTD MODULE_COMPRESS_ALL \
               SLAB_MERGE_DEFAULT LIST_HARDENED SCHED_POC_SELECTOR; do
        grep -qx "CONFIG_${opt}=y" .config || { echo "CONFIG_${opt} not set"; exit 1; }
    done
    for opt in UBSAN DEBUG_LIST KMALLOC_PARTITION_CACHES; do
        grep -qx "# CONFIG_${opt} is not set" .config || { echo "CONFIG_${opt} still set"; exit 1; }
    done

%build
    %make_build EXTRAVERSION=-%{release}.%{_arch} all

%install
    install -Dm644 "$(%make_build -s image_name)" "%{buildroot}%{_kernel_dir}/vmlinuz"
    zstdmt -19 < Module.symvers > %{buildroot}%{_kernel_dir}/symvers.zst
    ZSTD_CLEVEL=19 %make_build INSTALL_MOD_PATH="%{buildroot}" INSTALL_MOD_STRIP=1 DEPMOD=/doesnt/exist modules_install
    cp .config %{buildroot}%{_kernel_dir}/config
    cp System.map %{buildroot}%{_kernel_dir}/System.map

    rm -f %{buildroot}%{_kernel_dir}/build

    install -dm755 %{buildroot}/boot
    dd if=/dev/zero of=%{buildroot}/boot/initramfs-%{_kver}.img bs=1M count=90

%package core
Summary:        Linux BORE kernel
AutoReq:        no
Conflicts:      xfsprogs < 4.3.0-1
Conflicts:      xorg-x11-drv-vmmouse < 13.0.99
Provides:       kernel = %{_rpmver}
Provides:       kernel-core-uname-r = %{_kver}
Provides:       kernel-uname-r = %{_kver}
Provides:       installonlypkg(kernel)
Requires:       kernel-modules-uname-r = %{_kver}
Requires(pre):  /usr/bin/kernel-install
Requires(pre):  coreutils
Requires(pre):  dracut >= 027
Requires(pre):  systemd >= 203-2
Requires(pre):  ((linux-firmware >= 20150904-56.git6ebf5d57) if linux-firmware)
Requires(preun):systemd >= 200
Recommends:     linux-firmware

%description core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.

%post core
    mkdir -p %{_localstatedir}/lib/rpm-state/%{name}
    touch %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{_kver}

%posttrans core
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{_kver}
    if [ ! -e /run/ostree-booted ]; then
        /bin/kernel-install add %{_kver} %{_kernel_dir}/vmlinuz || exit $?
        if [[ ! -e "/boot/symvers-%{_kver}.zst" ]]; then
            cp "%{_kernel_dir}/symvers.zst" "/boot/symvers-%{_kver}.zst"
            if command -v restorecon &>/dev/null; then
                restorecon "/boot/symvers-%{_kver}.zst"
            fi
        fi
    fi

%preun core
    /bin/kernel-install remove %{_kver} || exit $?
    if [ -x /usr/sbin/weak-modules ]; then
        /usr/sbin/weak-modules --remove-kernel %{_kver} || exit $?
    fi

%files core
    %license COPYING
    %ghost %attr(0600, root, root) /boot/initramfs-%{_kver}.img
    %ghost %attr(0644, root, root) /boot/symvers-%{_kver}.zst
    %{_kernel_dir}/vmlinuz
    %{_kernel_dir}/modules.builtin
    %{_kernel_dir}/modules.builtin.modinfo
    %{_kernel_dir}/symvers.zst
    %{_kernel_dir}/config
    %{_kernel_dir}/System.map

%package modules
Summary:        Kernel modules for %{name}
Provides:       kernel-modules = %{_rpmver}
Provides:       kernel-modules-core = %{_rpmver}
Provides:       kernel-modules-extra = %{_rpmver}
Provides:       kernel-modules-uname-r = %{_kver}
Provides:       kernel-modules-core-uname-r = %{_kver}
Provides:       kernel-modules-extra-uname-r = %{_kver}
Provides:       installonlypkg(kernel-module)
Requires:       kernel-uname-r = %{_kver}

%description modules
Kernel modules for %{name}-core.

%post modules
    if [ ! -f %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{_kver} ]; then
        mkdir -p %{_localstatedir}/lib/rpm-state/%{name}
        touch %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver}
    fi

%posttrans modules
    rm -f %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver}
    /sbin/depmod -a %{_kver}
    if [ ! -e /run/ostree-booted ]; then
        if [ -f %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{_kver} ]; then
            dracut -f --kver "%{_kver}" || exit $?
        fi
    fi

%files modules
    %dir %{_kernel_dir}
    %{_kernel_dir}/modules.order
    %{_kernel_dir}/kernel

%files

%changelog
* Sat Oct 31 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.2.11-3.ludora
- Add the CachyOS POC (Piece-Of-Cake) idle CPU selector v2.6.3, as in
  kernel-ludora 7.2.11-100; next candidate for the remaining ~1.6% gap

* Fri Oct 30 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.2.11-2.ludora
- Disable UBSAN, DEBUG_LIST/BUG_ON_DATA_CORRUPTION and partitioned kmalloc
  caches, enable slab merging, matching kernel-ludora; candidate cause of
  the 1.6-2.7% CPU-side gap to kernel-ludora 7.2.11-100

* Thu Oct 29 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.2.11-1.ludora
- Build on 7.2.11 to match the last CachyOS 7.2 release (cachyos-7.2.11-1),
  so kernel-ludora and kernel-ludora-dev can be benchmarked on the same base
- Compress modules with zstd at install time so brp-strip no longer strips
  their signatures (unsigned modules are refused under Secure Boot)

* Thu Oct 29 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.2.13-1.ludora
- Update to kernel 7.2.13
- Release restarts at 1 (production kernel-ludora stays at 100)
- BORE patch checked against CachyOS 7.2 branch (unchanged)
- Apply usb-core C0 control-char string descriptor patch (was in the
  source tree but never applied)
- Port CachyOS's compiled-in CONFIG_CACHY defaults (swappiness, page-cluster,
  watermark boost, compaction, THP defrag, lru_gen min_ttl, readahead,
  split lock mitigation, bfq/mq-deadline, AMD bm_check_disable)
- Default transparent hugepages to always
- Enable RCU priority boosting
- Fail the build if any tuning option is dropped by Kconfig

* Sun Oct 25 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.2.12-200.ludora
- Update to kernel 7.2.12
- BORE patch re-fetched from CachyOS 7.2 branch
- Actually build for x86-64-v3: X86_64_VERSION does not exist in mainline,
  so previous builds were generic x86-64; set -march in arch/x86/Makefile
- Actually default to BBR: select DEFAULT_BBR (DEFAULT_TCP_CONG alone was
  reset to cubic by Kconfig)
- Apply usbhid uniq control-char patch (rebased onto 7.2.12)

* Wed Jul 22 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.1.4-200.ludora
- Update to kernel 7.1.4
- BORE patch verified against current CachyOS 7.1 branch (Piotr Gorski variant, unchanged since 7.1.3)

* Sun Jun 21 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.1.1-200.ludora
- Initial clean kernel.org + BORE build
