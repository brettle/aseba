Name:           aseba

# Update the following lines to reflect the source release version you will be
# referencing below
%global source_major 1
%global source_minor 3
%global source_patch 2
Version:        %{source_major}.%{source_minor}.%{source_patch}

# Update the following line with the git commit hash of the revision to use
# for example by running git show-ref -s --tags RELEASE_TAG
%global commit 952606f6f3309d71492321cdf794c761896fb018
%global shortcommit %(c=%{commit}; echo ${c:0:7})

# Update the following line to set commit_is_tagged_as_source_release to 0 if
# and only if the commit hash is not from a git tag for an existing source
# release (i.e. it is a commit hash for a pre-release or post-release
# revision). Otherwise set it to 1.
%global commit_is_tagged_as_source_release 0
%if %{commit_is_tagged_as_source_release} == 0
  %global snapshot .%(date +%%Y%%m%%d)git%{shortcommit}
%endif

# Update the number(s) in the "Release:" line below as follows. If this is 
# the first RPM release for a particular source release version, then set the
# number to 0. If this is the first RPM pre-release for a future source
# release version (i.e. the "Version:" line above refers to a future
# source release version), then set the number to 0.0. Otherwise, leave the
# the number unchanged. It will get bumped when you run rpmdev-bumpspec.
Release:        0.5%{?snapshot}%{?dist}
Summary:        A set of tools which allow beginners to program robots easily and efficiently

%global lib_pkg_name lib%{name}%{source_major}

%if 0%{?suse_version}
%global buildoutdir build
%else
%global buildoutdir .
%endif

%if 0%{?suse_version}
License:        LGPL-3.0
%else
License:        LGPLv3
%endif
URL:            http://aseba.wikidot.com
Source0:        https://github.com/aseba-community/aseba/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
Patch0:         aseba-rpm.patch

BuildRequires: ImageMagick
BuildRequires: ImageMagick-devel
BuildRequires: SDL-devel
BuildRequires: binutils
BuildRequires: cmake
BuildRequires: dashel-devel
BuildRequires: desktop-file-utils
BuildRequires: elfutils
BuildRequires: enki-devel
BuildRequires: file
BuildRequires: gdb
BuildRequires: glibc-devel
BuildRequires: kernel-headers
BuildRequires: libstdc++-devel
BuildRequires: libxml2-devel
%if 0%{?suse_version}
BuildRequires: hicolor-icon-theme
BuildRequires: Mesa-libGL-devel
BuildRequires: Mesa-libGLU-devel
# SUSE puts qcollectiongenerator in qt-devel-doc instead of qt-devel
BuildRequires: qt-devel-doc
%else
BuildRequires: mesa-libGL-devel
BuildRequires: mesa-libGLU-devel
%endif
BuildRequires: qt-devel
BuildRequires: qwt-devel
BuildRequires: gcc-c++
BuildRequires: doxygen


%description
Aseba is an event-based architecture for real-time distributed control of 
mobile robots. It targets integrated multiprocessor robots or groups of 
single-processor units, real or simulated. The core of aseba is a 
lightweight virtual machine tiny enough to run even on microcontrollers. 
With aseba, we program robots in a user-friendly programming language 
using a cozy integrated development environment.

%package -n %{lib_pkg_name}
Summary:        Libraries for %{name}
Group: System/Libraries

%description  -n %{lib_pkg_name}
The %{lib_pkg_name} package contains libraries running applications that use
%{name}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{lib_pkg_name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q -n %{name}-%{commit}
%patch0 -p1

%build
%cmake
make 
doxygen %{_builddir}/%{buildsubdir}/Doxyfile

%install
rm -rf $RPM_BUILD_ROOT
cd %{buildoutdir}
make install DESTDIR=$RPM_BUILD_ROOT
rm -rf ${RPM_BUILD_ROOT}%{_bindir}/asebatest
rm -rf ${RPM_BUILD_ROOT}%{_bindir}/aseba-test-natives-count
rm -rf ${RPM_BUILD_ROOT}%{_bindir}/asebashell
rm -rf ${RPM_BUILD_ROOT}%{_bindir}/qt-gui

cd examples
make clean
rm -rf *.cmake CMakeFiles Makefile 
rm -rf clients/*.cmake clients/CMakeFiles
rm -rf clients/*/*.cmake clients/*/CMakeFiles
cd %{_builddir}/%{buildsubdir}

install -d ${RPM_BUILD_ROOT}%{_datadir}/applications
install -d ${RPM_BUILD_ROOT}%{_datadir}/icons/hicolor/48x48/apps
cp menu/freedesktop/*.desktop ${RPM_BUILD_ROOT}%{_datadir}/applications
cp menu/freedesktop/*.png ${RPM_BUILD_ROOT}%{_datadir}/icons/hicolor/48x48/apps
convert ${RPM_BUILD_ROOT}%{_datadir}/icons/hicolor/48x48/apps/thymiovpl.png -resize 48x48 ${RPM_BUILD_ROOT}%{_datadir}/icons/hicolor/48x48/apps/thymiovpl.png
for file in ${RPM_BUILD_ROOT}%{_datadir}/applications/*.desktop; do
   sed -i 's|Icon=\(.*\).png|Icon=\1|g' $file
done

desktop-file-install --remove-category="Aseba" --dir=${RPM_BUILD_ROOT}%{_datadir}/applications ${RPM_BUILD_ROOT}%{_datadir}/applications/*.desktop

%check
#ctest

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%post -n %{lib_pkg_name}
/sbin/ldconfig

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%postun -n %{lib_pkg_name}
/sbin/ldconfig

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%doc debian/copyright debian/changelog readme.md targets/playground/unifr.playground targets/challenge/examples/challenge-goto-energy.aesl debian/README.Debian
%{_bindir}/*
%{_datadir}/applications/*
%{_datadir}/icons/hicolor/48x48/apps/*

%files -n %{lib_pkg_name}
%doc debian/copyright
%{_libdir}/*.so.*

%files devel
%doc %{buildoutdir}/doc/* examples/*
%{_includedir}/*
%{_libdir}/*.so

%changelog
* Wed Apr 16 2014 Dean Brettle <dean@brettle.com> - 1.3.2-0.5.20140416git96fb018
- Updated to latest 1.3.2 prerelease, added asebavmbuffer shared lib and headers,
  and made examples/clients buildable after installation.

* Mon Apr 14 2014 Dean Brettle <dean@brettle.com> - 1.3.2-0.4.20140414git8358704
- Added vm/*.h to the aseba-devel package.

* Fri Apr 11 2014 Dean Brettle <dean@brettle.com> - 1.3.2-0.4.20140411git8358704
- Updated to latest 1.3.2 prerelease and made some libs static and not installed.

* Mon Mar 03 2014 Dean Brettle <dean@brettle.com> - 1.3.2-0.3.20140303gitf44652d
- Updated spec to build on openSUSE and put libs in libaseba1 package.

* Sat Mar 01 2014 Dean Brettle <dean@brettle.com> - 1.3.2-0.2.20140228gitf44652d
- Changed SO_VERSION to SOVERSION so that libs only use major version number and
  added rpm directory with spec file and RPM building instructions.

* Thu Feb 27 2014 Dean Brettle <dean@brettle.com> - 1.3.2-0.1.20140223gitf44652d
- Built shared libs for additional -devel subpackage

* Sun Feb 23 2014 Dean Brettle <dean@brettle.com> - 1.3-1.20140223gitf44652d
- Initial release