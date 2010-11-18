%define enable_java		0
%define _requires_exceptions	libCg\\|libGL\\|libjack\\|libjawt\\|libXxf86vm

Name:		polymake
Summary:	Algorithms around polytopes and polyhedra
Version:	2.9.9
Release:	%mkrel 3
License:	GPL
Group:		Sciences/Mathematics
URL:		http://www.polymake.de/

%define topname %{name}-%{version}
Source:		ftp://ftp.math.tu-berlin.de/pub/combi/polymake-alpha/%{topname}.tar.bz2
Source1:	as3.gif

Provides:	perl(JavaView)
Provides:	perl(Polymake::Core::InteractiveCommands)
Provides:	perl(Polymake::Core::RuleFilter)
Provides:	perl(Polymake::Background)
Provides:	perl(Polymake::Namespaces)
Provides:	perl(Polymake::regex.pl)
Provides:	perl(Polymake::utils.pl)
Provides:	perl(Polymake::Sockets)

Requires:	make
Requires:	perl-devel
Requires:	perl >= 5.8.1 gcc-c++
Requires:	perl-XML-LibXML
Requires:	perl-XML-Writer
Requires:	perl-Term-ReadLine-Gnu
Requires:	singular
BuildRequires:	gmp-devel
BuildRequires:	perl-devel gcc-c++ libgmpxx-devel
BuildRequires:	perl-XML-Writer
BuildRequires:	perl-XML-LibXSLT

%if %{enable_java}
# libcg is in non free
Requires:	libcg
Requires:       java > 1.5
Requires:       jogl
BuildRequires:  java-rpmbuild
BuildRequires:	ant
%endif

BuildRequires:	xsltproc

Patch0:		int_max.patch
Patch1:		polymake-2.9.9-format.patch
Patch2:		polymake-2.9.9-make-3.82.patch
Patch3:		polymake-2.9.9-without-java.patch

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

%post
echo "Building perl extensions for polymake..."
[ -d $TMPDIR ] || TMPDIR=$HOME/tmp
[ -d $TMPDIR ] || exit 1
rm -rf $TMPDIR/%{name}-perlx
mkdir $TMPDIR/%{name}-perlx
pushd $TMPDIR/%{name}-perlx || exit 1
    export TOP=%{_datadir}/polymake
    /usr/bin/perl %{_datadir}/polymake/perl/ext/Makefile.PL
    make all pure_install InstallDir=%{_libdir}/polymake
popd
rm -rf $TMPDIR/%{name}-perlx

%triggerin -- perl
eval perl_`/usr/bin/perl -V:version`
if [ ! -d %{_libdir}/polymake/perlx/${perl_version} ]; then
    echo "Building perl extensions for polymake..."
    [ -d $TMPDIR ] || TMPDIR=$HOME/tmp
    [ -d $TMPDIR ] || exit 1
    rm -rf $TMPDIR/%{name}-perlx
    mkdir $TMPDIR/%{name}-perlx
    pushd $TMPDIR/%{name}-perlx || exit 1
	export TOP=%{_datadir}/polymake
	/usr/bin/perl %{_datadir}/polymake/perl/ext/Makefile.PL
	make all pure_install InstallDir=%{_libdir}/polymake
    popd
    rm -rf $TMPDIR/%{name}-perlx
fi

%preun
if [ $1 = 0 ]; then
   rm -rf %{_libdir}/polymake/perlx/*
fi

%prep
%setup -q -n %{topname}

%define ProjectTop %{_builddir}/%{topname}

%patch0	-p1
%patch1	-p1
%patch2	-p1

%if !%{enable_java}
%patch3 -p1
# do not cause it to link to or require 64 bit libraries
%endif

%build

if [ "%{_host_cpu}" = x86_64 -a "%{_target_cpu}" != x86_64 ]; then
  LDflags="LDFLAGS=-m32"
fi

./configure				\
	--prefix=%{_prefix} 		\
	--libdir=%{_libdir}/polymake	\
	--docdir=%{_docdir}/%{name}	\
        --build=%{_target_cpu}		\
%if !%{enable_java}
	--without-javaview		\
	--without-java			\
%endif
	CFLAGS="$(perl -e '$_=q{'"$RPM_OPT_FLAGS"'}; s/(?:^|\s)-(?:g|O\d)(?=\s|$)//g; print;')" $LDFLAGS
make Arch=%{_target_cpu} %{?_smp_mflags}%{?!_smp_mflags:%(NCPUS=`grep -c '^processor' /proc/cpuinfo`; [ -n "$NCPUS" -a "$NCPUS" -gt 1 ] && echo -j$NCPUS )} ProcessDep=n

%install
make Arch=%{_target_cpu} PREFIX=%{_prefix} DESTDIR=%{buildroot} install docs
perl support/install.pl -m 755 perl/ext %{buildroot}%{_datadir}/%{name}/perl/ext
mkdir -p %{buildroot}%{_libdir}/polymake/perlx
cp -fa %{SOURCE1} %{buildroot}%{_datadir}/%{name}

# give write permissions to owner so that strip works
find %{buildroot}%{_libdir} | xargs chmod u+w

find %{buildroot}%{_libdir} -name \*.so | xargs chmod a-x

%if %{enable_java}
    %ifarch x86_64 ppc64
	rm -fr %{buildroot}%{_libdir}/%{name}/jreality/jni/linux32
    %else
	rm -fr %{buildroot}%{_libdir}/%{name}/jreality/jni/linux64
    %endif
%else
    rm -fr %{buildroot}%{_libdir}/%{name}/lib/jreality
%endif
