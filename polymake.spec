# $Project: polymake $$Id: polymake.spec 9097 2009-02-22 22:48:46Z gawrilow $

Summary: Algorithms around polytopes and polyhedra
Name: polymake
Version: 2.9.6
Release: 1
License: GPL
Group: Applications/Sciences/Mathematics
URL: http://www.math.tu-berlin.de/polymake/
Vendor: TU Berlin, Algorithmic and Discrete Mathematics
Packager: TU Berlin, Algorithmic and Discrete Mathematics <polymake@math.tu-berlin.de>
Icon: as3.gif

%define topname %{name}-%{version}
Source: ftp://ftp.math.tu-berlin.de/pub/combi/polymake-alpha/%{topname}.tar.bz2
Requires: perl >= 5.8.1 gcc-c++ perl(XML::LibXML) perl(XML::SAX::Base) perl(XML::Writer) perl(XML::LibXSLT) perl(Term::ReadLine::Gnu)
BuildRequires: perl gcc-c++ gmp
Prefix: /usr

%description
Polymake is a versatile tool for the algorithmic treatment of
polytopes and polyhedra.  It offers an unified interface to a wide
variety of algorithms and free software packages from the computational
geometry field, such as convex hull computation or visualization tools.

The 2.9 series are test versions towards the "next generation" polymake.
They introduce an interactive shell, the XML-base file format, more
efficient C++/perl interface, and many other new features.

%files
%attr(-, bin, bin) /usr/bin/polymake
%attr(-, bin, bin) /usr/share/polymake
%attr(-, bin, bin) %dir /usr/%{_lib}/polymake
%attr(-, bin, bin) %dir /usr/%{_lib}/polymake/perlx
%attr(-, bin, bin) /usr/%{_lib}/polymake/lib
%attr(-, bin, bin) %config /usr/%{_lib}/polymake/conf.make

%define guess_prefix : ${RPM_INSTALL_PREFIX:=%{_prefix}} ${RPM_INSTALL_PREFIX:=$RPM_INSTALL_PREFIX0} ${RPM_INSTALL_PREFIX:=/usr}

# RPM still does not understand line continuations in spec files!

%define build_perlx echo "Building perl extensions for polymake...";  : ${TMPDIR:=%{_tmppath}} ${TMPDIR:=/var/tmp};  rm -rf $TMPDIR/%{topname}-perlx;  mkdir $TMPDIR/%{topname}-perlx;  pushd $TMPDIR/%{topname}-perlx;  TOP=$RPM_INSTALL_PREFIX/share/polymake /usr/bin/perl $RPM_INSTALL_PREFIX/share/polymake/perl/ext/Makefile.PL;  make all pure_install InstallDir=$RPM_INSTALL_PREFIX/%{_lib}/polymake;  popd;  rm -rf $TMPDIR/%{topname}-perlx

%post
%{guess_prefix}
%{build_perlx}

if [ "$RPM_INSTALL_PREFIX" != /usr ]; then
   /usr/bin/perl -i -p -e 's|(PREFIX=).*|$1'$RPM_INSTALL_PREFIX'|' $RPM_INSTALL_PREFIX/%{_lib}/polymake/conf.make
fi


%triggerin -- perl
%{guess_prefix}

eval perl_`/usr/bin/perl -V:version`
if [ ! -d $RPM_INSTALL_PREFIX/%{_lib}/polymake/perlx/${perl_version} ]; then
  %{build_perlx}
fi


%preun
%{guess_prefix}

if [ $1 = 0 ]; then
   rm -rf $RPM_INSTALL_PREFIX/%{_lib}/polymake/perlx/*
fi


%prep
%setup -q -n %{topname}

%define ProjectTop %{_builddir}/%{topname}

%build
# won't build without java support
export PATH=%{_libdir}/jvm/java-openjdk/bin:$PATH
Cflags=$(perl -e '$_=q{'"$RPM_OPT_FLAGS"'}; s/(?:^|\s)-(?:g|O\d)(?=\s|$)//g; print;')

{
   echo Cflags=$Cflags
   echo CXXflags=$Cflags
   if [ "%{_host_cpu}" = x86_64 -a "%{_target_cpu}" != x86_64 ]; then
      echo LDflags=-m32
   fi
   echo InstallTop=/usr/share/polymake
   echo InstallArch=/usr/%{_lib}/polymake
   echo InstallDoc=/usr/share/doc/polymake
   echo InstallBin=/usr/bin
   echo ProcessDep=none
   echo JavaBuild=
   echo Arch=%{_target_cpu}
} | make configure

make ProjectTop=%{ProjectTop} Arch=%{_target_cpu} %{?_smp_mflags}%{?!_smp_mflags:%(NCPUS=`grep -c '^processor' /proc/cpuinfo`; [ -n "$NCPUS" -a "$NCPUS" -gt 1 ] && echo -j$NCPUS )}


%install
make ProjectTop=%{ProjectTop} Arch=%{_target_cpu} PREFIX=/usr ${RPM_BUILD_ROOT:+DESTDIR=$RPM_BUILD_ROOT} install
perl -i -p -e 's|(Install\w+=)/usr|$1\${PREFIX}|' $RPM_BUILD_ROOT/usr/%{_lib}/polymake/conf.make
perl support/install.pl -m 755 perl/ext $RPM_BUILD_ROOT/usr/share/polymake/perl/ext
mkdir $RPM_BUILD_ROOT/usr/%{_lib}/polymake/perlx

%define __find_provides %{ProjectTop}/support/find-provides
