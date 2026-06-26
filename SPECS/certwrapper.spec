%global package_speccommit e48c702f53ee15249e05a168c6fa51f45b0e27a6
%global usver 20240117
%global xsver 8
%global xsrel %{xsver}%{?xscount}%{?xshash}
%global package_srccommit c443a5fa7210f2dcd12e2b0825e70fda16592d4e

# Disable debuginfo package since RPM cannot extract debuginfo from
# the PE binary.
%global debug_package %{nil}

Name: certwrapper
Version: 20240117
Release: %{?xsrel}%{?dist}
Summary: Contains certificates for Secure Boot
License: BSD-2-Clause-Patent

URL: https://github.com/rhboot/certwrapper
Source0: certwrapper-20240117.tar.gz
Source1: revocations.csv
Patch0: set-sbat-data.patch
Patch1: revocations.patch
Patch2: set-nx_compat.patch

BuildRequires: gcc
BuildRequires: nss-tools
BuildRequires: efitools
BuildRequires: gnu-efi-devel
BuildRequires: openssl
BuildRequires: sbsigntools
BuildRequires: xcpsign-macros-test

%description
This package contains certificates for Secure Boot, packaged in an EFI
binary. The certificates are used by Shim.

%prep
%autosetup -p1

%build
> db.esl
for cert in GRUB_SIGN_KEY_XCP9 XEN_SIGN_KEY_XCP9 LINUX_SIGN_KEY_XCP9; do
    %fetchcert -c "$cert" -o "${cert}.cer"
    openssl x509 -inform der -in "${cert}.cer" -outform pem -out "${cert}.crt"
    cert-to-efi-sig-list "${cert}.crt" "${cert}.esl"
    cat "${cert}.esl" >> db.esl
done

sed -i -e 's/@@VERSION@@/%{version}/g' -e 's/@@RELEASE@@/%{release}/g' data/sbat.csv

cp %{SOURCE1} data/revocations.csv

make CFLAGS="-I/usr/include/efi"

%sign -c SHIM_EMBEDDED_SIGN_KEY_XCP9 -i certwrapper.efi -o certwrapper-signed.efi
%sign -c SHIM_EMBEDDED_SIGN_KEY_XCP9 -i revocations.efi -o revocations-signed.efi


%install
mkdir -p %{buildroot}/boot/efi/EFI/xenserver
install -m 755 certwrapper-signed.efi %{buildroot}/boot/efi/EFI/xenserver/shim_certificate_0.efi
install -m 755 revocations-signed.efi %{buildroot}/boot/efi/EFI/xenserver/revocations.efi

%files
/boot/efi/EFI/xenserver/*

%changelog
* Wed Jun 10 2026 Corentin Oparowski <corentin.oparowski@vates.tech> - 20240117-8
- Changed certs for test with xcp-ng
- Update dependencies to xcpsign-macros-test
- [WIP] Change source for revocations.csv

* Wed Oct 08 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 20240117-7
- CP-47917: Re-sign with new key

* Thu Aug 21 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 20240117-6
- CP-308091: Set NX_COMPAT flag

* Fri Jul 04 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 20240117-5
- Update SBAT email address

* Wed May 21 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 20240117-4
- Simplify signing build dependencies to just xssign-macros

* Thu Apr 17 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 20240117-3
- CP-49469: Depend on python3-xssign

* Mon Mar 17 2025 Ross Lagerwall <ross.lagerwall@citrix.com> - 20240117-2
- CP-53944: Make compatible with shim 16

* Mon Mar 11 2024 Ross Lagerwall <ross.lagerwall@citrix.com> - 20240117-1
- Initial packaging
