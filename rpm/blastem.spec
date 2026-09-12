%global commit 2dd605c6e27971f67ce5b8363cc858964f99aa50
%global shortcommit 2dd605c
%global commitdate 20260821

Name:           blastem
Version:        0.6.3~pre^%{commitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Sega Genesis and Mega Drive emulator

# BlastEm is GPL-3.0-or-later. The built GUI embeds public-domain Nuklear code
# and MIT-licensed code and font data. Installed shaders include GPL-3.0-only
# and MIT-licensed code, and the controller database is Zlib-licensed.
License:        GPL-3.0-or-later AND GPL-3.0-only AND MIT AND Zlib AND LicenseRef-Fedora-Public-Domain
# The snapshot also contains unused Apache-2.0 Gradle wrapper files.
SourceLicense:  GPL-3.0-or-later AND GPL-3.0-only AND Apache-2.0 AND MIT AND Zlib AND LicenseRef-Fedora-Public-Domain
URL:            https://www.retrodev.com/blastem
ExclusiveArch:  x86_64

# Generated reproducibly from the exact commit above by rpm-builder's
# git_archive strategy; see rpm/README.source in the packaging branch.
Source0:        %{name}-%{commit}.tar.gz
Source1:        com.retrodev.BlastEm.desktop
Source2:        com.retrodev.BlastEm.metainfo.xml
Source3:        com.retrodev.BlastEm.png
Source4:        blastem.6
Source5:        THIRD-PARTY-LICENSES
Source6:        README.Fedora

Patch0:         0001-build-respect-distribution-flags.patch
Patch1:         0002-build-use-system-zlib-headers.patch
Patch2:         0003-build-support-a-private-termhelper-path.patch
Patch3:         0004-debugger-use-private-per-launch-fifos.patch

BuildRequires:  appstream
BuildRequires:  desktop-file-utils
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glew)
BuildRequires:  pkgconfig(gtk+-3.0)
# Fedora 44's sdl2-compat-devel provides this API and capability.
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  pkgconfig(zlib)

# The native chooser is loaded with dlopen(), so ELF dependency generation
# cannot discover it. Font lookup similarly invokes fc-match at runtime.
Requires:       fontconfig
Requires:       gtk3%{?_isa}
Requires:       hicolor-icon-theme
# The interactive debugger asks the desktop's configured terminal to run the
# private bridge helper. This executable dependency is not visible to ELF RPM
# dependency generation.
Requires:       xdg-terminal-exec

%description
BlastEm emulates the Sega Genesis and Mega Drive, Sega and Mega CD, 32X,
Master System and Mark III, Game Gear, SG-1000, and SC-3000 systems. It
provides a graphical interface, save states, controller mapping, debugging,
and OpenGL shader support.

No commercial game ROMs, console firmware, or BIOS images are included.

%prep
%autosetup -n %{name}-%{commit} -p1

# Fedora uses its system zlib. Removing the bundled implementation makes an
# accidental fallback visible at build time. The prebuilt Gradle wrapper is
# unrelated to this native desktop build.
rm -rf zlib android/gradle/wrapper/gradle-wrapper.jar

cp -p %{SOURCE5} THIRD-PARTY-LICENSES
cp -p %{SOURCE6} README.Fedora

# Make the application's version output identify this exact snapshot.
sed -i 's/0\.6\.3-pre/0.6.3-pre-%{commitdate}git%{shortcommit}/' version.inc

%build
%set_build_flags
# NOLTO suppresses only upstream's unconditional bare -flto. Fedora's
# toolchain-selected LTO flags remain present through the environment CFLAGS.
%make_build blastem termhelper \
    CC=%{__cc} \
    CPU=x86_64 \
    HOST_ZLIB=1 \
    NOLTO=1 \
    DATA_PATH=%{_datadir}/%{name} \
    TERMHELPER_PATH=%{_libexecdir}/%{name}/termhelper

%install
install -Dpm0755 blastem %{buildroot}%{_bindir}/blastem
install -Dpm0755 termhelper \
    %{buildroot}%{_libexecdir}/%{name}/termhelper

install -d %{buildroot}%{_datadir}/%{name}
install -pm0644 default.cfg gamecontrollerdb.txt rom.db systems.cfg \
    %{buildroot}%{_datadir}/%{name}/
cp -a images shaders %{buildroot}%{_datadir}/%{name}/

install -Dpm0644 %{SOURCE1} \
    %{buildroot}%{_datadir}/applications/com.retrodev.BlastEm.desktop
install -Dpm0644 %{SOURCE2} \
    %{buildroot}%{_metainfodir}/com.retrodev.BlastEm.metainfo.xml
install -Dpm0644 %{SOURCE3} \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/com.retrodev.BlastEm.png
install -Dpm0644 %{SOURCE4} %{buildroot}%{_mandir}/man6/blastem.6

%check
desktop-file-validate \
    %{buildroot}%{_datadir}/applications/com.retrodev.BlastEm.desktop
appstreamcli validate --no-net \
    %{buildroot}%{_metainfodir}/com.retrodev.BlastEm.metainfo.xml

test_home=$PWD/.test-home
mkdir -p "$test_home/.config/blastem"
cp -p default.cfg "$test_home/.config/blastem/blastem.cfg"
HOME="$test_home" ./blastem -v | \
    grep -F 'blastem 0.6.3-pre-%{commitdate}git%{shortcommit}'
HOME="$test_home" ./blastem -h | grep -F 'Usage: blastem'
grep -aF '%{_datadir}/%{name}' blastem >/dev/null
grep -aF '%{_libexecdir}/%{name}/termhelper' blastem >/dev/null
grep -aF 'xdg-terminal-exec' blastem >/dev/null
grep -aF '/tmp/blastem.XXXXXX' blastem >/dev/null
! grep -aF '/tmp/blastem_input' blastem termhelper >/dev/null
! grep -aF '/tmp/blastem_output' blastem termhelper >/dev/null

%files
%license COPYING THIRD-PARTY-LICENSES
%doc CHANGELOG README README.Fedora
%{_bindir}/blastem
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/termhelper
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/default.cfg
%{_datadir}/%{name}/gamecontrollerdb.txt
%{_datadir}/%{name}/rom.db
%{_datadir}/%{name}/systems.cfg
%dir %{_datadir}/%{name}/images
%{_datadir}/%{name}/images/*.png
%dir %{_datadir}/%{name}/shaders
%{_datadir}/%{name}/shaders/*.glsl
%{_datadir}/applications/com.retrodev.BlastEm.desktop
%{_metainfodir}/com.retrodev.BlastEm.metainfo.xml
%{_datadir}/icons/hicolor/256x256/apps/com.retrodev.BlastEm.png
%{_mandir}/man6/blastem.6*

%changelog
* Fri Sep 11 2026 Reaper <JohnGrimmReaper@disroot.org> - 0.6.3~pre^20260821git2dd605c-1
- Package the 2026-08-21 upstream snapshot
- Use Fedora build flags and system libraries
- Add native desktop, AppStream, and filesystem integration
- Secure native debugger helper startup
