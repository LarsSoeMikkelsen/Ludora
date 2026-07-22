Name:           goverlay
Version:        1.8.9
Release:        %autorelease
Epoch:          2
Summary:        Project that aims to create a Graphical UI to help manage Linux overlays
ExclusiveArch:  %{fpc_arches}
#%%global commit 85476e05bb768dc4e9e0b0f02afbd6bcbf394e5a

License:        GPLv3+
URL:            https://github.com/benjamimgois/goverlay
Source0:        %{url}/archive/refs/tags/%{version}/%{name}-%{version}.tar.gz
Patch0:         goverlay-enable-debuginfo-generation.patch

BuildRequires:  desktop-file-utils
BuildRequires:  fpc-srpm-macros
BuildRequires:  lazarus
BuildRequires:  lazarus-lcl-qt6
BuildRequires:  libappstream-glib
BuildRequires:  libglvnd-devel
BuildRequires:  make
BuildRequires:  sdl2-compat-devel

Requires:       hicolor-icon-theme
Requires:       mangohud%{?_isa}
Requires:       mesa-libGLU
Requires:       qt6pas%{?_isa}
Requires:       /usr/bin/lsb_release

# git - Clone reshade repository
Recommends:     git%{?_isa}

Recommends:     mesa-demos%{?_isa}
Recommends:     vkBasalt%{?_isa}
Recommends:     vulkan-tools%{?_isa}

%description
GOverlay is an open source project aimed to create a Graphical UI to manage
Vulkan/OpenGL overlays. It is still in early development, so it lacks a lot of
features.

This project was only possible thanks to the other maintainers and
contributors that have done the hard work. I am just a Network Engineer that
really likes Linux and Gaming.


%prep
%autosetup -p1 -n %{name}-%{version}


%build
%set_build_flags
mkdir -p ~/.lazarus
cp /etc/lazarus/environmentoptions.xml ~/.lazarus/environmentoptions.xml
%make_build


%install
%make_install prefix=%{_prefix}


%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/%{name}/assets/
%{_datadir}/%{name}/bgmod/
%{_datadir}/%{name}/data/
%{_libexecdir}/%{name}
%{_libexecdir}/pascube
%{_libexecdir}/bgmod
%{_libexecdir}/bgmod-uninstaller
%{_mandir}/man1/*.1*
%{_metainfodir}/*.xml
