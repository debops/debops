#!/bin/bash

# bootstrap-ansible.sh: download and build Ansible on Debian/Ubuntu host

# Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2014-2017 DebOps https://debops.org/


# This program is free software; you can redistribute
# it and/or modify it under the terms of the
# GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General
# Public License along with this program; if not,
# write to the Free Software Foundation, Inc., 59
# Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# An on-line copy of the GNU General Public License can
# be downloaded from the FSF web page at:
# https://www.gnu.org/copyleft/gpl.html


# Usage: ./bootstrap-ansible.sh [branch] [build_directory]


set -e

install_ansible_requirements () {

    sudo apt-get --no-install-recommends -qq -y install git devscripts \
        python-paramiko python-yaml python-jinja2 python-httplib2 \
        cdbs debhelper dpkg-dev fakeroot sshpass python-nose python-passlib \
        python-setuptools asciidoc xmlto build-essential python-sphinx \
        python-crypto lsb-release

}

build_ansible_deb () {

    # Build Debian package
    if [ -n "$(grep 'local_deb' Makefile || true)" ] ; then
        LANG=C make local_deb
    else
        LANG=C make deb
    fi

    # Check if .deb package with new method is present
    if [ -n "$(find deb-build/unstable/ -name ansible_*_all.deb 2>/dev/null)" ]; then

        sudo dpkg -i deb-build/unstable/ansible_*_all.deb

    # Otherwise, look for package generated with old method
    elif [ -n "$(find .. -name ansible_*_all.deb 2>/dev/null)" ]; then

        sudo dpkg -i ../ansible_*_all.deb

    fi

}

bootstrap_ansible_deb () {

    local ansible_branch="${1:-devel}"
    local build_dir="${2:-$(mktemp -d)}"
    local ansible_git_repo="${3:-https://github.com/ansible/ansible}"

    local ansible_source_dir="ansible"

    if [ ! -d "${build_dir}" ] ; then
        mkdir -p "${build_dir}"
    fi

    cd "${build_dir}"

    if [ -d "${ansible_source_dir}" ] ; then

        cd "${ansible_source_dir}"

        local old_git_checkout="$(git rev-parse HEAD)"

        local current_branch_name="$(git symbolic-ref HEAD 2>/dev/null)" ||
        local current_branch_name="(unnamed branch)"     # detached HEAD
        local current_branch_name=${current_branch_name##refs/heads/}

        if [ "${current_branch_name}" != "${ansible_branch}" ] ; then
            git checkout "${ansible_branch}"
        fi

        git pull --quiet
        git submodule update

        local current_git_checkout="$(git rev-parse HEAD)"

        if [ "${old_git_checkout}" != "${current_git_checkout}" ] ; then
            build_ansible_deb
        fi

    else

        install_ansible_requirements
        git clone --branch "${ansible_branch}" --recursive "${ansible_git_repo}" "${ansible_source_dir}"
        cd "${ansible_source_dir}"
        build_ansible_deb

    fi
}

ansible_branch="${1:-devel}"
build_dir="${2:-$(mktemp -d)}"

bootstrap_ansible_deb "${ansible_branch}" "${build_dir}"
