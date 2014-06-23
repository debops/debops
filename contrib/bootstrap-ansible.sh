#!/bin/bash

# bootstrap-ansible.sh: download and build Ansible on Debian host
# https://github.com/ginas/ginas/

set -e

# Ansible project repository to use
project="git://github.com/ansible/ansible.git"

# Select branch to build
branch="${1:-devel}"

# Create temporary directory for build
build_dir=$(mktemp -d)
trap "rm -rf ${build_dir}" EXIT

cd ${build_dir}

# Update APT package database
sudo apt-get update

# Install required packages
sudo apt-get --no-install-recommends -q -y install git devscripts \
	python-paramiko python-yaml python-jinja2 python-httplib2 \
	cdbs debhelper dpkg-dev python-support fakeroot sshpass \
	python-nose python-passlib python-setuptools asciidoc xmlto \
	build-essential

# Clone Ansible from main project repository (devel branch, default)
git clone --branch ${branch} ${project} ansible
cd ansible

# Build Debian package
make deb

version=$(cat VERSION)

# Install Debian package
if [[ "${branch}" != "devel" ]]; then
	sudo dpkg -i ../ansible_${version}_all.deb
else
	sudo dpkg -i deb-build/unstable/ansible_${version}-*_all.deb
fi


