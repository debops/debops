# Build and install DebOps on the Arch Linux host
#
# Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017 DebOps project https://debops.org/

# To install DebOps on Arch Linux, after cloning the repository, run:
#
#     makepkg -si
#
# This will install all of the required dependencies, then build and install
# the DebOps Python package.
#
# After installation, run 'debops-update' to download or update the
# role/playbook code from GitHub. The DebOps monorepo will be downloaded in
# '~/.local/share/debops/debops/' directory on your user account.


# Maintainer: Maciej Delmanowski <drybjed@gmail.com>
pkgname=debops-git
_pkgname=debops
pkgver=VERSION
pkgrel=1
pkgdesc="Your Debian-based data center in a box"
arch=('any')
url="https://github.com/debops/debops/"
license=('GPL3')
depends=('python' 'python-distro' 'python-future' 'util-linux' 'encfs' 'gnupg')
optdepends=(
    'ansible: required to run playbooks and roles'
    'python-dnspython: required by Ansible "dig" module'
    'python-pyopenssl: required by "openssl_*" Ansible modules'
    'python-netaddr: required by Ansible "ipaddr" filter plugin'
    'python-ldap: required by Ansible "ldap_*" modules'
    'python-passlib: required by Ansible "password" lookup plugin')
makedepends=('python-setuptools' 'git')
provides=('debops')
conflicts=('debops')
source=("$_pkgname::git+https://github.com/debops/debops")
sha256sums=('SKIP')

pkgver() {
    cd "$_pkgname"
    git describe --long --tags | sed 's/\([^-]*-g\)/r\1/;s/-/./g' | sed 's/v//'
}

build() {
    cd "$_pkgname"
    python setup.py build
}

package() {
    cd "$_pkgname"
    python setup.py install --root="$pkgdir" --optimize=1
}
