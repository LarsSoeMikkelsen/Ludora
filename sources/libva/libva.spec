#global pre_release .pre1

Name:		libva
Version:	2.23.0
Release:	%autorelease
Summary:	Video Acceleration (VA) API for Linux
# va/wayland/wayland-drm.xml is HPND-sell-variant
# va/x11/va_dri* are ICU
License:	MIT AND HPND-sell-variant AND ICU
URL:		https://github.com/intel/libva
Source0:	%{url}/archive/%{version}%{?pre_release}/%{name}-%{version}%{?pre_release}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc

BuildRequires:	libudev-devel
%{!?_without_xorg:
BuildRequires:	libXext-devel
BuildRequires:	libXfixes-devel
}
BuildRequires:	libdrm-devel
BuildRequires:	libpciaccess-devel
BuildRequires:	mesa-libEGL-devel
BuildRequires:	mesa-libGL-devel
BuildRequires:	mesa-libGLES-devel
%{!?_without_wayland:
BuildRequires:  wayland-devel
BuildRequires:  pkgconfig(wayland-client) >= 1
BuildRequires:  pkgconfig(wayland-scanner) >= 1
}
# owns the %%{_libdir}/dri directory
Requires:	mesa-filesystem%{_isa}

%description
Libva is a library providing the VA API video acceleration API.

%package	devel
Summary:	Development files for %{name}
Requires:	%{name}%{_isa} = %{version}-%{release}

%description	devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%autosetup -p1 -n %{name}-%{version}%{?pre_release}

%build
%meson \
 -Dwith_legacy=nvctrl \
 -Ddriverdir="%{_libdir}/dri-nonfree:%{_libdir}/dri-freeworld:%{_libdir}/dri" \
%{?_without_xorg: -Dwith_glx=no -Dwith_x11=no} \
%{?_without_wayland: -Dwith_wayland=no}

%meson_build

%install
%meson_install

# Don't break assumption, set driverdir as one single dir
sed -i -e 's|driverdir=.*|driverdir=%{_libdir}/dri|' %{buildroot}%{_libdir}/pkgconfig/libva.pc

# Owns the alternates directories
mkdir -p %{buildroot}%{_libdir}/dri-{freeworld,nonfree}


%ldconfig_scriptlets

%files
%doc NEWS
%license COPYING
%ghost %{_sysconfdir}/libva.conf
%dir %{_libdir}/dri-*
%{_libdir}/libva.so.2*
%{_libdir}/libva-drm.so.2*
%{!?_without_wayland:
%{_libdir}/libva-wayland.so.2*
}
%{!?_without_xorg:
%{_libdir}/libva-x11.so.2*
%{_libdir}/libva-glx.so.2*
}

%files devel
%{_includedir}/va
%{_libdir}/libva*.so
%{_libdir}/pkgconfig/libva*.pc

%changelog
%autochangelog
