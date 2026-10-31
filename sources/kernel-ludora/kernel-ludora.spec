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
%define _basekver 7.3
%define _stablekver 1
# 7.3.x already sorts above the last CachyOS-based kernel-ludora
# (7.2.11-100, sources/kernel), so the release can start at 1
%define _releasekver 1
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

Name:           kernel-ludora
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

# BORE and POC come straight from their author (firelzrd / Masahito Suzuki),
# not from CachyOS. Pinned commits; re-fetch for each kernel series:
# https://github.com/firelzrd/bore-scheduler 1e2f57ad74e8 patches/stable/
Patch0:         0001-linux7.3-rc2-bore-7.0.0.patch
Patch1:         0001-hid-usbhid-sanitize-uniq-against-control-chars.patch
Patch2:         0001-usb-core-truncate-string-descriptors-at-first-C0-con.patch
Patch3:         0001-cachyos-default-tunables.patch
# Piece-Of-Cake idle CPU selector
# https://github.com/firelzrd/poc-selector 5c5a0c897208 patches/stable/
# v2.6.3 is only published for 7.2 but applies to 7.3; the 7.3 patch is
# v3.0.0, still marked testing upstream (not benchmarked or reviewed)
Patch4:         0001-7.2-rc1-poc-selector-v2.6.3.patch

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

    # Drop Fedora's debug/hardening options that the old CachyOS-based kernel
    # also leaves off: UBSAN instruments every array access and shift,
    # DEBUG_LIST checks every list op (BUG_ON_DATA_CORRUPTION selects it;
    # LIST_HARDENED stays), and partitioned kmalloc caches plus no slab
    # merging spread allocations over more caches
    scripts/config -d UBSAN -d BUG_ON_DATA_CORRUPTION -d DEBUG_LIST \
                   -d KMALLOC_PARTITION_CACHES -e SLAB_MERGE_DEFAULT

    # Faster idle CPU search on wakeup (POC selector, Patch4)
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

    # Development files (headers, Makefiles, built host tools) for building
    # out-of-tree modules (akmods/DKMS, e.g. NVIDIA). Same file list as
    # the old CachyOS-based kernel-ludora, which follows Fedora's kernel.spec; bpftool vmlinux.h is
    # left out (not needed for modules, would need clang)
    install -Dt %{buildroot}%{_devel_dir} -m644 .config Makefile Module.symvers System.map
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}%{_devel_dir}
    rm -rf %{buildroot}%{_devel_dir}/scripts
    rm -rf %{buildroot}%{_devel_dir}/include
    cp -a scripts %{buildroot}%{_devel_dir}
    rm -rf %{buildroot}%{_devel_dir}/scripts/tracing
    rm -f %{buildroot}%{_devel_dir}/scripts/spdxcheck.py

    # Needed for `make scripts`
    cp -a --parents security/selinux/include/classmap.h %{buildroot}%{_devel_dir}
    cp -a --parents security/selinux/include/initial_sid_to_string.h %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/tools/be_byteshift.h %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/tools/le_byteshift.h %{buildroot}%{_devel_dir}

    # Needed for `make prepare` -- generic
    cp -a --parents tools/include/linux/compiler* %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/linux/types.h %{buildroot}%{_devel_dir}
    cp -a --parents tools/build/Build.include %{buildroot}%{_devel_dir}
    cp --parents tools/build/fixdep.c %{buildroot}%{_devel_dir}
    cp --parents tools/objtool/sync-check.sh %{buildroot}%{_devel_dir}
    cp -a --parents tools/bpf/resolve_btfids %{buildroot}%{_devel_dir}

    cp --parents security/selinux/include/policycap_names.h %{buildroot}%{_devel_dir}
    cp --parents security/selinux/include/policycap.h %{buildroot}%{_devel_dir}

    cp -a --parents tools/include/asm %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/asm-generic %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/linux %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/asm %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/asm-generic %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/uapi/linux %{buildroot}%{_devel_dir}
    cp -a --parents tools/include/vdso %{buildroot}%{_devel_dir}
    cp --parents tools/scripts/utilities.mak %{buildroot}%{_devel_dir}
    cp -a --parents tools/lib/subcmd %{buildroot}%{_devel_dir}
    cp --parents tools/lib/*.c %{buildroot}%{_devel_dir}
    cp --parents tools/objtool/*.[ch] %{buildroot}%{_devel_dir}
    cp --parents tools/objtool/Build %{buildroot}%{_devel_dir}
    cp --parents tools/objtool/include/objtool/*.h %{buildroot}%{_devel_dir}
    cp -a --parents tools/lib/bpf %{buildroot}%{_devel_dir}
    cp --parents tools/lib/bpf/Build %{buildroot}%{_devel_dir}

    # Misc headers
    cp -a --parents arch/x86/include %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/include %{buildroot}%{_devel_dir}
    cp -a include %{buildroot}%{_devel_dir}/include
    cp -a sound/soc/sof/sof-audio.h %{buildroot}%{_devel_dir}/sound/soc/sof
    cp -a tools/objtool/objtool %{buildroot}%{_devel_dir}/tools/objtool/
    cp -a tools/objtool/fixdep %{buildroot}%{_devel_dir}/tools/objtool/

    # Needed for `make prepare` -- x86_64
    cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_32.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_64.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs_common.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/tools/relocs.h %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/purgatory.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/stack.S %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/setup-x86_64.S %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/purgatory/entry64.S %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/boot/string.h %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/boot/string.c %{buildroot}%{_devel_dir}
    cp -a --parents arch/x86/boot/ctype.h %{buildroot}%{_devel_dir}

    cp -a --parents scripts/syscalltbl.sh %{buildroot}%{_devel_dir}
    cp -a --parents scripts/syscallhdr.sh %{buildroot}%{_devel_dir}

    cp -a --parents tools/arch/x86/include/asm %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/include/uapi/asm %{buildroot}%{_devel_dir}
    cp -a --parents tools/objtool/arch/x86/lib %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/lib/ %{buildroot}%{_devel_dir}
    cp -a --parents tools/arch/x86/tools/gen-insn-attr-x86.awk %{buildroot}%{_devel_dir}
    cp -a --parents tools/objtool/arch/x86/ %{buildroot}%{_devel_dir}

    find %{buildroot}%{_devel_dir}/scripts \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
    find %{buildroot}%{_devel_dir}/tools \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +
    touch -r %{buildroot}%{_devel_dir}/Makefile \
        %{buildroot}%{_devel_dir}/include/generated/uapi/linux/version.h \
        %{buildroot}%{_devel_dir}/include/config/auto.conf

    # The build-time module signing key (certs/signing_key.pem) must never
    # ship: anyone holding it could sign modules this kernel trusts
    if grep -rlq -- "-----BEGIN .*PRIVATE KEY-----" %{buildroot}%{_devel_dir}; then
        echo "private key found in devel files:"
        grep -rl -- "-----BEGIN .*PRIVATE KEY-----" %{buildroot}%{_devel_dir}
        exit 1
    fi

    # build/source links live in -devel, so they only exist when the
    # headers they point at are installed
    rm -f %{buildroot}%{_kernel_dir}/build
    ln -s %{_devel_dir} %{buildroot}%{_kernel_dir}/build
    ln -s %{_kernel_dir}/build %{buildroot}%{_kernel_dir}/source

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

%package devel
Summary:        Development package for building kernel modules to match %{name}
Provides:       kernel-devel = %{_rpmver}
Provides:       kernel-devel-uname-r = %{_kver}
Provides:       installonlypkg(kernel)
AutoReqProv:    no
Requires(pre):  findutils
Requires:       findutils
Requires:       perl-interpreter
Requires:       openssl-devel
Requires:       elfutils-libelf-devel
Requires:       bison
Requires:       flex
Requires:       make

%description devel
Kernel headers and makefiles sufficient to build modules against %{name}.

%post devel
    if [ -f /etc/sysconfig/kernel ]; then
        . /etc/sysconfig/kernel || exit $?
    fi
    if [ "$HARDLINK" != "no" -a -x /usr/bin/hardlink -a ! -e /run/ostree-booted ]; then
        (cd /usr/src/kernels/%{_kver} &&
        /usr/bin/find . -type f | while read f; do
            hardlink -c /usr/src/kernels/*%{?dist}.*/$f $f > /dev/null
        done;
        )
    fi

%files devel
    %{_devel_dir}
    %{_kernel_dir}/build
    %{_kernel_dir}/source

%package devel-matched
Summary:        Meta package to install matching core and devel packages for %{name}
Provides:       kernel-devel-matched = %{_rpmver}
Requires:       %{name}-core = %{_rpmver}
Requires:       %{name}-devel = %{_rpmver}

%description devel-matched
Installs matching core and devel packages for %{name}.

%files devel-matched

%files

%changelog
* Sat Oct 31 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.3.1-1.ludora
- kernel-ludora is now this kernel (previously kernel-ludora-dev): kernel.org
  source plus BORE and POC from their author, no CachyOS code. Replaces the
  CachyOS-based kernel-ludora 7.2.11-100 (sources/kernel)
- Update to kernel 7.3.1
- BORE 7.0.0: firelzrd stable patch for 7.3 (same commit 1e2f57ad74e8)
- POC selector v2.6.3 kept (7.2 patch, applies to 7.3)
- Tunables patch rebased: page_cluster moved to mm/swap_state.c, split lock
  hunk has new context; values unchanged

* Sat Oct 31 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.2.11-5.ludora
- Add -devel and -devel-matched subpackages (headers for akmods/DKMS,
  e.g. NVIDIA), same file list as kernel-ludora; build/source links
  owned by -devel; fail the build if a private key lands in -devel
- No kernel changes vs 7.2.11-4

* Sat Oct 31 2026 Lars Soe Mikkelsen <larssoemikkelsen@gmail.com> - 7.2.11-4.ludora
- Take BORE and POC directly from firelzrd instead of CachyOS
- BORE 6.8.0-rc1 (CachyOS rebase) -> 7.0.0; adds wakeup sleep credit
  (kernel.sched_credit_cap_us, default 16000)
- POC selector v2.6.3 unchanged (same code as the CachyOS commits)

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
