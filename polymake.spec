%define _requires_exceptions	libCg\\|libGL\\|libjack\\|libjawt\\|libXxf86vm

Name:		polymake
Summary:	Algorithms around polytopes and polyhedra
Version:	2.9.9
Release:	%mkrel 1
License:	GPL
Group:		Sciences/Mathematics
URL:		http://www.polymake.de/

%define topname %{name}-%{version}
Source:		ftp://ftp.math.tu-berlin.de/pub/combi/polymake-alpha/%{topname}.tar.bz2
Source1:	as3.gif
Requires:       java > 1.5
Requires:       jogl
Requires:	perl-devel
Requires:	singular
Requires:	libcg
Requires:	perl >= 5.8.1 gcc-c++
Requires:	perl-XML-LibXML
Requires:	perl-XML-Writer
Requires:	perl-Term-ReadLine-Gnu
Provides:	perl(JavaView)
Provides:	perl(Polymake::Core::InteractiveCommands)
Provides:	perl(Polymake::Core::RuleFilter)
Provides:	perl(Polymake::Background)
Provides:	perl(Polymake::Namespaces)
Provides:	perl(Polymake::regex.pl)
Provides:	perl(Polymake::utils.pl)
Provides:	perl(Polymake::Sockets)
BuildRequires:	gmp-devel
BuildRequires:	perl-devel gcc-c++ libgmpxx-devel
BuildRequires:	perl-XML-Writer
BuildRequires:	perl-XML-LibXSLT
BuildRequires:  java-rpmbuild
BuildRequires:	ant

Patch0:		int_max.patch
Patch1:		polymake-2.9.9-format.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Polymake is a versatile tool for the algorithmic treatment of
polytopes and polyhedra.  It offers a unified interface to a wide
variety of algorithms and free software packages from the computational
geometry field, such as convex hull computation or visualization tools.

The 2.9 series are test versions towards the "next generation" polymake.
They introduce an interactive shell, the XML-base file format, more
efficient C++/perl interface, and many other new features.

%files
%defattr(-,root,root,-)
%{_bindir}/polymake
%{_datadir}/polymake
%dir %{_libdir}/polymake
%dir %{_libdir}/polymake/perlx
%{_libdir}/polymake/lib
%config %{_libdir}/polymake/conf.make
%doc %{_docdir}/%{name}

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

%patch0	-p1
%patch1	-p1

%build

if [ "%{_host_cpu}" = x86_64 -a "%{_target_cpu}" != x86_64 ]; then
  LDflags="LDFLAGS=-m32"
fi

./configure				\
	--prefix=%{_prefix} 		\
	--libdir=%{_libdir}/polymake	\
	--docdir=%{_docdir}/%{name}	\
        --build=%{_target_cpu}		\
	CFLAGS="$(perl -e '$_=q{'"$RPM_OPT_FLAGS"'}; s/(?:^|\s)-(?:g|O\d)(?=\s|$)//g; print;')" $LDFLAGS
make Arch=%{_target_cpu} %{?_smp_mflags}%{?!_smp_mflags:%(NCPUS=`grep -c '^processor' /proc/cpuinfo`; [ -n "$NCPUS" -a "$NCPUS" -gt 1 ] && echo -j$NCPUS )} ProcessDep=n

%install
make Arch=%{_target_cpu} PREFIX=%{_prefix} DESTDIR=%{buildroot} install docs
perl support/install.pl -m 755 perl/ext %{buildroot}%{_datadir}/%{name}/perl/ext
mkdir -p %{buildroot}%{_libdir}/polymake/perlx
cp -fa %{SOURCE1} %{buildroot}%{_datadir}/%{name}

# give write permissions to owner so that strip works
find %{buildroot}%{_libdir} | xargs chmod u+w
