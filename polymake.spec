%define		_enable_debug_packages	%{nil}
%define		debug_package		%{nil}

%bcond_without	java

%if %{_use_internal_dependency_generator}
%define __noautoreq 'libCg(.*)|libGL(.*)|libjack(.*)|libjawt(.*)|libXxf86vm(.*)|libX11(.*)'
%else
%define _requires_exceptions	libCg\\|libGL\\|libjack\\|libjawt\\|libXxf86vm.so.1\\|libX11.so.6
%endif

Name:		polymake
Summary:	Algorithms around polytopes and polyhedra
Version:	2.12
Release:	1
License:	GPL
Group:		Sciences/Mathematics
URL:		http://www.polymake.org/

Source:		http://www.polymake.org/lib/exe/fetch.php/download/%{name}-%{version}-rc3.tar.bz2
Source1:	as3.gif

Provides:	perl(JavaView)
Provides:	perl(Polymake::Core::InteractiveCommands)
Provides:	perl(Polymake::Core::RuleFilter)
Provides:	perl(Polymake::Background)
Provides:	perl(Polymake::Namespaces)
Provides:	perl(Polymake::regex.pl)
Provides:	perl(Polymake::utils.pl)
Provides:	perl(Polymake::Sockets)
Provides:	perl(Polymake::regex.pl)
Provides:	perl(Polymake::utils.pl)

Requires:	gcc-c++
Requires:	gmpxx-devel
Requires:	mpfr-devel
Requires:	java >= 1.5
Requires:	perl-devel
Requires:	perl(XML::LibXML)
Requires:	perl(XML::SAX::Base)
Requires:	perl(XML::Writer)
Requires:	perl(XML::LibXSLT)
Requires:	perl(Term::ReadLine::Gnu)
BuildRequires:	gcc-c++
BuildRequires:	gmpxx-devel
BuildRequires:	mpfr-devel
BuildRequires:	boost-devel
BuildRequires:	libxml2-devel
%if %{with java}
Suggests:	libcg
BuildRequires:	java-devel >= 1.5
BuildRequires:	jogl
BuildRequires:	java-rpmbuild
BuildRequires:	ant >= 1.7.1
%endif
BuildRequires:	perl-devel
BuildRequires:	xmlto
BuildRequires:	xsltproc
BuildRequires:	xhtml1-dtds
BuildRequires:	perl(XML::LibXML)
BuildRequires:	perl(XML::SAX::Base)
BuildRequires:	perl(XML::Writer)
BuildRequires:	perl(ExtUtils::MakeMaker)

Patch0:		polymake-2.11-format.patch

%description
Polymake is a versatile tool for the algorithmic treatment of
polytopes and polyhedra.  It offers an unified interface to a wide
variety of algorithms and free software packages from the computational
geometry field, such as convex hull computation or visualization tools.

%files
%{_bindir}/polymake
%{_bindir}/polymake-config
%{_includedir}/polymake
%{_datadir}/polymake
%dir %{_libdir}/polymake
%{_libdir}/polymake/lib
%{_libdir}/polymake/perlx
%{_libdir}/libpolymake.so
%config %{_libdir}/polymake/conf.make
%doc %{_docdir}/polymake

#----------------------------------------------------------------------------

%prep
%setup -q

%patch0 -p1

%build
Cflags=`echo %{optflags} |				\
    sed	-e 's/\(-Wp,\)\?-D_FORTIFY_SOURCE=[12]//g'	\
	-e 's/-gdwarf-4//'				\
	-e 's/-Wa,--compress-debug-sections//'		\
	-e 's/-fvar-tracking-assignments//'		\
	-e 's/-frecord-gcc-switches//'`
Cflags=`echo "$Cflags" | sed -e 's/[[:blank:]]\+/ /g'`
Cflags="$Cflags -pthread"
LDflags="-lxml2 -lpthread -ldl"
./configure					\
	--prefix=%{_prefix}			\
	--libdir=%{_libdir}			\
	--libexecdir=%{_libdir}/polymake	\
	--docdir=%{_docdir}/%{name}		\
	--build=%{_target_cpu}			\
	--without-prereq			\
%if %{without java}
	--without-javaview			\
	--without-java				\
%endif
	CC=gcc					\
	CXX=g++					\
	CXXOPT=-O2				\
	CFLAGS="$Cflags"			\
	CXXFLAGS="$Cflags"			\
	LDFLAGS="$LDflags"
make Arch=%{_target_cpu} ProcessDep=n

%install
make Arch=%{_target_cpu} PREFIX=%{_prefix} DESTDIR=%{buildroot} install release-docs
cp -fa %{SOURCE1} %{buildroot}%{_datadir}/%{name}

# give write permissions to owner so that strip works
find %{buildroot}%{_libdir} | xargs chmod u+w
find %{buildroot}%{_libdir} -name \*.so | xargs chmod a-x

%if %{with java}
    %ifarch x86_64 ppc64
	rm -fr %{buildroot}%{_libdir}/%{name}/lib/jreality/jni/linux32
    %else
	rm -fr %{buildroot}%{_libdir}/%{name}/lib/jreality/jni/linux64
    %endif
%else
    rm -fr %{buildroot}%{_libdir}/%{name}/lib/jreality
%endif

