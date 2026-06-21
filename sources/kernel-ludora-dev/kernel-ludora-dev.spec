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
%define _basekver 7.1
%define _stablekver 1
%define _releasekver 200
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

    %if %{_x86_64_lvl} < 5 && %{_x86_64_lvl} > 0
        scripts/config --set-val X86_64_VERSION %{_x86_64_lvl}
    %else
        echo "Invalid x86_64 ISA Level. Using x86_64_v3"
        scripts/config --set-val X86_64_VERSION 3
    %endif

    # Gaming tuning
    # Full static preemption — lower latency than Fedora's PREEMPT_DYNAMIC/LAZY default
    scripts/config -d PREEMPT_NONE -d PREEMPT_VOLUNTARY -d PREEMPT_LAZY -d PREEMPT_DYNAMIC -e PREEMPT

    # BBR built-in and default — better latency under load than cubic
    scripts/config -e TCP_CONG_BBR --set-str DEFAULT_TCP_CONG bbr

    # FQ built-in — pairs with BBR for per-flow pacing
    scripts/config -e NET_SCH_FQ

    # LATENCYTOP adds per-task latency tracking overhead with no gaming benefit
    scripts/config -d LATENCYTOP

    # NUMA auto-balancing adds latency jitter on single-socket systems
    scripts/config -d NUMA_BALANCING_DEFAULT_ENABLED

%build
    %make_build EXTRAVERSION=-%{release}.%{_arch} all

%install
    install -Dm644 "$(%make_build -s image_name)" "%{buildroot}%{_kernel_dir}/vmlinuz"
    zstdmt -19 < Module.symvers > %{buildroot}%{_kernel_dir}/symvers.zst
    ZSTD_CLEVEL=19 %make_build INSTALL_MOD_PATH="%{buildroot}" INSTALL_MOD_STRIP=1 DEPMOD=/doesnt/exist modules_install
    cp .config %{buildroot}%{_kernel_dir}/config
    cp System.map %{buildroot}%{_kernel_dir}/System.map

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
