%{?scl:%scl_package %{name}}

%if 0%{?fedora} || 0%{?rhel} == 6|| 0%{?rhel} == 7
%global with_devel 1
%global with_bundled 0
%global with_debug 0
# test fails
%global with_check 0
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%define copying() \
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7 \
%license %{*} \
%else \
%doc %{*} \
%endif

%global provider        github
%global provider_tld    com
%global project         go-check
%global repo            check
# https://github.com/go-check/check
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     gopkg.in/check.v1
%global import_path_sec launchpad.net/gocheck
%global commit          91ae5f88a67b14891cfd43895b01164f6c120420
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

# github.com/motain/gocheck, cloned from github.com/go-check/check on Oct 23, 2013
%global mcommit         10bfe0586b48cbca10fe6c43d6e18136f25f8c0c
%global mscommit        %(c=%{mcommit}; echo ${c:0:7})
%global mimport_path    github.com/motain/gocheck

Name:           %{?scl_prefix}golang-gopkg-%{repo}
Version:        0
Release:        7%{?dist}
Summary:        Rich testing for the Go language
License:        BSD
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{mcommit}/%{repo}-%{mscommit}.tar.gz
Source1:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz
Obsoletes:      golang-launchpad-gocheck

# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check}
%endif


Provides:      %{?scl_prefix}golang(%{import_path}) = %{version}-%{release}
Provides:      %{?scl_prefix}golang(%{import_path_sec}) = %{version}-%{release}
Provides:      %{?scl_prefix}golang(%{mimport_path}) = %{version}-%{release}
Obsoletes:     golang-launchpad-gocheck-devel

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test}
%package unit-test
Summary:         Unit tests for %{name} package
# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -n %{repo}-%{mcommit} -q
%setup -n %{repo}-%{commit} -q -T -b 1

%build
%{?scl:scl enable %{scl} - << "EOF"}

%{?scl:EOF}
%install
%{?scl:scl enable %{scl} - << "EOF"}
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
install -d -p %{buildroot}/%{gopath}/src/%{import_path_sec}/
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path_sec}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{import_path_sec}/$file
    echo "%%{gopath}/src/%%{import_path_sec}/$file" >> devel.file-list
done
pushd ../%{repo}-%{mcommit}
install -d -p %{buildroot}/%{gopath}/src/%{mimport_path}/
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{mimport_path}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{mimport_path}/$file
    echo "%%{gopath}/src/%%{mimport_path}/$file" >> ../%{repo}-%{commit}/devel.file-list
done
popd
%endif

# testing files for this project
%if 0%{?with_unit_test}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%if 0%{?with_devel}
olddir=$(pwd)
pushd %{buildroot}/%{gopath}/src/%{import_path}
for file in $(find . -type d) ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$file" >> ${olddir}/devel.file-list
done
popd
echo "%%dir %%{gopath}/src/gopkg.in" >> devel.file-list

sort -u -o devel.file-list devel.file-list
%endif

%if 0%{?with_devel}
olddir=$(pwd)
pushd %{buildroot}/%{gopath}/src/%{import_path_sec}
for file in $(find . -type d) ; do
    echo "%%dir %%{gopath}/src/%%{import_path_sec}/$file" >> ${olddir}/devel.file-list
done
popd
echo "%%dir %%{gopath}/src/launchpad.net" >> devel.file-list

sort -u -o devel.file-list devel.file-list
%endif

%if 0%{?with_devel}
olddir=$(pwd)
pushd %{buildroot}/%{gopath}/src/%{mimport_path}
for file in $(find . -type d) ; do
    echo "%%dir %%{gopath}/src/%%{mimport_path}/$file" >> ${olddir}/devel.file-list
done
popd
echo "%%dir %%{gopath}/src/github.com/motain" >> devel.file-list
echo "%%dir %%{gopath}/src/github.com" >> devel.file-list

sort -u -o devel.file-list devel.file-list
%endif

%{?scl:EOF}
%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%ifarch 0%{?gccgo_arches}
function gotest { %{gcc_go_test} "$@"; }
%else
%if 0%{?golang_test:1}
function gotest { %{golang_test} "$@"; }
%else
function gotest { go test "$@"; }
%endif
%endif

export GOPATH=%{buildroot}/%{gopath}:%{gopath}
gotest %{import_path}
%endif

%if 0%{?with_devel}
%files devel -f devel.file-list
%copying LICENSE
%doc README.md
%endif

%if 0%{?with_unit_test}
%files unit-test -f unit-test.file-list
%copying LICENSE
%doc README.md
%endif

%changelog
* Wed Feb 3 2016 Marek Skalicky <mskalick@redhat.com> - 0-7
- Fixed directory ownership

* Wed Jul 29 2015 jchaloup <jchaloup@redhat.com> - 0-6
- Update of spec file to spec-2.0
  resolves: #1248138

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jan 13 2015 jchaloup <jchaloup@redhat.com> - 0-4
- Add github.com/motain/gocheck into Provides
  related: #1151779

* Tue Jan 13 2015 jchaloup <jchaloup@redhat.com> - 0-3
- Add github.com/motain/gocheck into devel subpackage
  related: #1151779

* Tue Dec 09 2014 jchaloup <jchaloup@redhat.com> - 0-2
- Obsolete golang-launchpad-gocheck-devel with devel subpackage
  related: #1151779

* Fri Oct 10 2014 Jan Chaloupka <jchaloup@redhat.com> - 0-1
- First package for Fedora
