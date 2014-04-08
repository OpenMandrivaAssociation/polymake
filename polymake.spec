# TESTING NOTE: "make test" does not work, because the test drivers are not
# distributed with the released sources.  A Subversion repository containing
# all of the sources, including the test drivers, was made available recently.
# Once the next release of polymake occurs, we will extract the necessary test
# drivers from subversion and produce a check script.

# If a library used by both polymake and Singular is updated, neither can be
# rebuilt, because each BRs the other and both are linked against the old
# version of the library.  Use this to rebuild polymake without Singular
# support, rebuild Singular, then build polymake again with Singular support.
%bcond_without singular

# Date of the "perpetual beta" subversion snapshot
%global svndate 20140326

Name:           polymake
Version:        2.12
Release:        15.svn%{svndate}%{?dist}
Summary:        Algorithms on convex polytopes and polyhedra

License:        GPLv2+
URL:            http://polymake.org/
#Source0:        http://polymake.org/lib/exe/fetch.php/download/%%{name}-%%{version}%%{rctag}.tar.bz2
# Sources taken from the polymake "perpetual beta".  Create the tarball thusly:
#   svn checkout --username "guest" --password "" http://polymake.mathematik.tu-darmstadt.de/svn/polymake/snapshots/%{svndate} polymake-%{version}
#   rm -fr polymake-%{version}/.svn polymake-%{version}/external/{cdd,lrs}
#   rm -fr polymake-%{version}/bundled/jreality/external/jreality/.svn
#   tar cjf polymake-%{version}.tar.bz2 polymake-%{version}
Source0:        %{name}-%{version}.tar.bz2
# Man page written by Jerry James from text found in the sources.  Therefore,
# the copyright and license are the same as for the sources.
Source1:        %{name}.1
Source2:        %{name}.rpmlintrc
# This patch will not be sent upstream, since it is Fedora-specific.  Link
# against existing system libraries instead of building them from source,
# and do not use -rpath.
Patch0:         %{name}-fedora.patch
# This patch was sent upstream 20 Mar 2013.  Fix a call to an lrslib function
# that segfaults when given a NULL argument.
Patch1:         %{name}-lrslib.patch
# Avoid -Werror=format-security failures.
Patch2:         %{name}-format.patch
# Adapt to the old version of Singular in Fedora.  Remove this once the
# Singular package is updated to version 3-1-6 or later.
Patch3:         %{name}-singular.patch

BuildRequires:  bliss-devel
BuildRequires:  boost-devel
BuildRequires:  cddlib-devel
BuildRequires:  cmake
BuildRequires:  eigen3-static
BuildRequires:  libnormaliz-devel
BuildRequires:  libxml2-devel
BuildRequires:  lrslib-devel
BuildRequires:  mpfr-devel
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(JSON::PP)
BuildRequires:  perl(Term::ReadLine::Gnu)
BuildRequires:  perl(XML::LibXSLT)
BuildRequires:  perl(XML::SAX::Base)
BuildRequires:  perl(XML::Writer)
BuildRequires:  perl-devel
BuildRequires:  ppl-devel
BuildRequires:  sympol-devel
BuildRequires:  xhtml1-dtds
%if %{with singular}
BuildRequires:  singular-devel
%endif

Requires:       perl(:MODULE_COMPAT_%{perl_version})
Requires:       perl = 4:%{perl_version}
Requires:       perl(Term::ReadLine::Gnu)

%global sover   %(echo %{version} | cut -d. -f1-2)
%global major   %(echo %{version} | cut -d. -f1)
%global polydir %{_libdir}/%{name}

# Don't expose private perl interfaces
%global __noautoreq 'perl\(Geomview.*\)'
%global __noautoreq '%{__noautoreq}|perl\(Graphviz.*\)'
%global __noautoreq '%{__noautoreq}|perl\(Metapost.*\)'
%global __noautoreq '%{__noautoreq}|perl\(PerlIO.*\)'
%global __noautoreq '%{__noautoreq}|perl\(Postscript.*\)'
%global __noautoreq '%{__noautoreq}|perl\(Povray.*\)'
%global __noautoreq '%{__noautoreq}|perl\(Sketch.*\)'
%global __noautoreq '%{__noautoreq}|perl\(SplitsTree.*\)'
%global __noautoreq '%{__noautoreq}|perl\(application\)'
%global __noautoreq '%{__noautoreq}|perl\(_.*\)'

# Exclude private perl interfaces that we don't Provide
%global __noautoprov 'perl\(it\)
%global __noautoprov '%{__noautoprov}|perl\(Polymake::Background\)'
%global __noautoprov '%{__noautoprov}|perl\(Polymake::Core::RuleFilter\)'
%global __noautoprov '%{__noautoprov}|perl\(Polymake::file_utils\.pl\)'
%global __noautoprov '%{__noautoprov}|perl\(Polymake::Namespaces\)'
%global __noautoprov '%{__noautoprov}|perl\(Polymake::regex\.pl\)'
%global __noautoprov '%{__noautoprov}|perl\(Polymake::utils\.pl\)'

%description
Polymake is a tool to study the combinatorics and the geometry of convex
polytopes and polyhedra.  It is also capable of dealing with simplicial
complexes, matroids, polyhedral fans, graphs, tropical objects, and so
forth.

Polymake can use various computational packages if they are installed.
Those available from Fedora are: 4ti2, azove, gfan, latte-integrale,
normaliz, ocaml-tplib-tools, qhull, Singular, TOPCOM, and vinci.

Polymake can interface with various visualization packages if they are
installed.  Install one or more of the tools from the following list:
evince, geomview, graphviz, gv, and okular.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains header files and libraries for developing
plugins (applications) that use %{name}.

%package doc
Summary:        Documentation for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description doc
This package contains documentation for %{name}.

%prep
%setup -q
%patch0
%patch1
%patch2
%patch3

# Make sure we don't build against the bundled libraries.
rm -fr external/{cdd,lrs}

# Adapt to a newer version of sympol
sed -i "s|yal/||;s|symmetrygroupconstruction/||" \
    bundled/group/apps/polytope/src/sympol_interface.cc

%build
mkdir bin
pushd bin
    ln -sf %{_bindir}/ld.bfd ld
popd
export PATH=$PWD/bin:$PATH
export CFLAGS="$RPM_OPT_FLAGS -I%{_includedir}/eigen3 -I%{_includedir}/singular -Wno-unused-local-typedefs -fuse-ld=bfd"
export CXXFLAGS="$CFLAGS"
export LDFLAGS="$RPM_LD_FLAGS -Wl,--as-needed -ldl"
export Arch=%{_arch}
# NOT an autoconf-generated configure script; do not use %%configure.
./configure --build=%{_arch} --prefix=%{_prefix} --libdir=%{_libdir} \
  --libexecdir=%{polydir} --without-java --without-javaview
make %{?_smp_mflags} all

# Help the debuginfo generator find generated files
cd build.%{_arch}
cp -p perlx-*linux-*/CPlusPlus.xxs lib/core/CPlusPlus.xxs
cp -p perlx-*linux-*/CPlusPlus.cc lib/core/CPlusPlus.cc

%install
# Don't recompile the main library with DESTDIR compiled in
sed -i "/conf\.make/d" support/corelib.make

# The release-docs target copies docs to their installed locations
export Arch=%{_arch}
make install release-docs DESTDIR=%{buildroot}

# The apps have undefined weak symbols.  However, fixing that kills the
# documentation building step for reasons I can't seem to track down.  So
# instead, we wait until after the docs have been generated, then relink.
sed -e 's|^Libs :=.*|& -L$(wildcard ${BuildDir}/perlx-*-linux-*) -lpolymake|' \
    -i support/app.make
sed -e 's|-lgmp ${LIBS}|& -L${PerlExtDir} -lpolymake|' \
    -e 's|^${CoreLib} :.*|& ${CallableLib}|' \
    -i support/corelib.make
rm -f build.%{_arch}/lib/*.so
make %{?_smp_mflags} all
chmod 0755 %{buildroot}%{polydir}/lib/*.so
cp -p build.%{_arch}/lib/*.so %{buildroot}%{polydir}/lib

# Install the man page
mkdir -p %{buildroot}%{_mandir}/man1
sed "s/@VERSION@/%{version}/" %{SOURCE1} > %{buildroot}%{_mandir}/man1/%{name}.1
touch -r %{SOURCE1} %{buildroot}%{_mandir}/man1/%{name}.1

# We don't want the documentation in /usr/share/polymake
mv %{buildroot}%{_datadir}/%{name}/doc .

# Remove stuff that shouldn't be installed
rm -fr %{buildroot}%{_datadir}/%{name}/apps/*/src \
  %{buildroot}%{_datadir}/%{name}/java_build \
  %{buildroot}%{polydir}/perlx/*/*/auto/Polymake/Ext/{.packlist,Ext.bs} \
  %{buildroot}%{polydir}/lib/jreality

# Fix permissions
chmod 0755 %{buildroot}%{_bindir}/*
chmod 0755 %{buildroot}%{_libdir}/lib*
find %{buildroot}%{polydir} -name \*.so | xargs chmod 0755

# Remove the buildroot from configuration files
sed -i 's,%{buildroot},,' %{buildroot}%{polydir}/bundled/bliss/conf.make
sed -i 's,%{buildroot},,' %{buildroot}%{polydir}/bundled/group/conf.make
sed -i 's,%{buildroot},,' %{buildroot}%{polydir}/bundled/libnormaliz/conf.make
sed -i 's,%{buildroot},,' %{buildroot}%{polydir}/bundled/ppl/conf.make
%if %{with singular}
sed -i 's,%{buildroot},,' %{buildroot}%{polydir}/bundled/singular/conf.make
%endif

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_libdir}/lib%{name}*.so.*
%{polydir}/
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/lib/

%files devel
%{_bindir}/%{name}-config
%{_includedir}/%{name}/
%{_datadir}/%{name}/lib/
%{_libdir}/lib%{name}*.so

%files doc
%doc doc/*

%changelog
* Wed Apr  2 2014 Jerry James <loganjerry@gmail.com> - 2.12-15.svn20140326
- Update to latest "perpetual beta" for bug fixes
- Add conditional to build without Singular support

* Wed Mar 12 2014 Jerry James <loganjerry@gmail.com> - 2.12-14.svn20131128
- Build with Singular support
- Make transitive dependency on eigen3 (via sympol) explicit

* Sat Jan 18 2014 Jerry James <loganjerry@gmail.com> - 2.12-13.svn20131128
- Update Requires filters

* Fri Jan 17 2014 Jerry James <loganjerry@gmail.com> - 2.12-12.svn20131128
- Update to latest "perpetual beta" for bug fixes
- Enable building new ppl and libnormaliz extensions

* Wed Jan  8 2014 Jerry James <loganjerry@gmail.com> - 2.12-11.svn20130813
- Rebuild for perl 5.18.2
- Add -format patch to fix -Werror=format-security failure

* Wed Aug 14 2013 Jerry James <loganjerry@gmail.com> - 2.12-10.svn20130813
- Update to latest "perpetual beta" for perl 5.18 compatibility (bz 992813)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.12-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 24 2013 Petr Pisar <ppisar@redhat.com> - 2.12-8
- Perl 5.18 rebuild

* Sun Jul 21 2013 Rich Mattes <richmattes@gmail.com> - 2.12-7
- Rebuild for eigen3-3.1.3

* Wed May 15 2013 Jerry James <loganjerry@gmail.com> - 2.12-6
- Require version of perl used to build (bz 963486)
- perl(Term::ReadLine::Gnu) dependency is not autogenerated (bz 963486)

* Wed Mar 20 2013 Jerry James <loganjerry@gmail.com> - 2.12-5
- Add -lrslib patch to fix a segfault (bz 923269)

* Wed Feb 27 2013 Jerry James <loganjerry@gmail.com> - 2.12-4
- Remove rpath and -L%%{_libdir} from polymake-config --ldflags output

* Thu Jan 24 2013 Jerry James <loganjerry@gmail.com> - 2.12-3
- Also need to filter perl(Graphviz)

* Wed Jan 23 2013 Jerry James <loganjerry@gmail.com> - 2.12-2
- Change -libs patch to also remove -rpath arguments
- Filter Provides/Requires to hide private perl interfaces
- Remove the broken check script and explain why

* Thu Jan 10 2013 Jerry James <loganjerry@gmail.com> - 2.12-1
- Initial RPM
