#!/bin/bash

# bootstrap-ansible.sh: download and build Ansible on Debian host
# https://github.com/ginas/ginas/

set -e

# Create temporary directory for build
build_dir=$(mktemp -d)
trap "rm -rf ${build_dir}" EXIT

cd ${build_dir}

# Install required packages
sudo apt-get --no-install-recommends -q -y install git \
	python-paramiko python-yaml python-jinja2 python-httplib2 \
	cdbs debhelper dpkg-dev python-support fakeroot sshpass \
	python-nose python-passlib asciidoc

# Clone Ansible from main project repository (devel branch, default)
git clone git://github.com/ansible/ansible.git ansible
cd ansible

# Build Debian package
make deb

version=$(cat VERSION)

# Install Debian package
sudo dpkg -i ../ansible_${version}_all.deb


