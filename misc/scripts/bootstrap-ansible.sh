#!/bin/sh

# bootstrap-ansible.sh: download and build Ansible on Debian/Ubuntu host
# Copyright (C) 2014 Maciej Delmanowski <drybjed@gmail.com>
# Part of the DebOps project - http://debops.org/


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
# http://www.gnu.org/copyleft/gpl.html


# By default, script will install latest 'devel' branch of Ansible; to specify
# different branch or tag, specify it as the first argument


set -e

# Ansible project repository to use
project="https://github.com/ansible/ansible.git"

# Select branch to build
branch="${1:-devel}"

# Create temporary directory for build
build_dir=$(mktemp -d)
trap "rm -rf ${build_dir}" EXIT

cd ${build_dir}

# Update APT package database
sudo apt-get update -qq

# Install required packages
sudo apt-get --no-install-recommends -qq -y install git devscripts \
	python-paramiko python-yaml python-jinja2 python-httplib2 \
	cdbs debhelper dpkg-dev python-support fakeroot sshpass \
	python-nose python-passlib python-setuptools asciidoc xmlto \
	build-essential

# Clone Ansible from main project repository (devel branch, default)
git clone --branch ${branch} --recursive ${project} ansible
cd ansible

# Build Debian package
make deb

version=$(cat VERSION)

# Check if .deb package with new method is present
if [ -n "$(find deb-build/unstable/ -name ansible_${version}-*_all.deb 2>/dev/null)" ]; then
	sudo dpkg -i deb-build/unstable/ansible_${version}-*_all.deb

# Otherwise, look for package generated with old method
elif [ -n "$(find .. -name ansible_${version}_all.deb 2>/dev/null)" ]; then
	sudo dpkg -i ../ansible_${version}_all.deb
fi


