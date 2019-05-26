#!/usr/bin/env bash

# Filter specified PHP package names to the corresponding APT package names
# available on the system.
# Homepage: https://github.com/debops/ansible-php/

# Usage:
# Specify the PHP version in the $PHP_VERSION environment variable, either '5'
# or '7.0'. Only one PHP version is supported at a time.

# Specify the list of package names without the 'php5-' or 'php7.0-' prefix
# as script arguments.


set -o pipefail -o errexit

# Look for the PHP packages of a particular version
php_version="${PHP_VERSION:-5}"

# List of packages to filter
search_packages=( "$@" )

# List of available PHP packages in APT repositories
mapfile -t package_list < <( apt-cache pkgnames php ; apt-cache --no-generate pkgnames libapache2-mod-php )


# The fast way to search through the list in Bash is to use an associative
# array. First, create the array with all available package names as keys
declare -A available_packages

for name in "${package_list[@]}" ; do
    available_packages["${name}"]=1
done

# Then, check if a specific key exists in the array
for element in "${search_packages[@]}" ; do

    # Support for 'php<version>-*' packages
    if [[ ${available_packages["php${php_version}-${element}"]} ]] ; then
        echo "php${php_version}-${element}"

    # Support for 'php-*' packages
    elif [[ ${available_packages["php-${element}"]} ]] ; then
        echo "php-${element}"

    # Support for 'libapache2-mod-php<version>' package
    elif [[ ${available_packages["${element}${php_version}"]} ]] ; then
        echo "${element}${php_version}"

    # Support for other packages
    else
        if [ -n "${element}" ] ; then
            echo "${element}"
        fi
    fi

done
