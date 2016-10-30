#!/bin/bash

set -o pipefail -o errexit

php_version="${PHP_VERSION:-5}"

search_packages="${@:-}"

package_list=( $(apt-cache --no-generate pkgnames php ; apt-cache --no-generate pkgnames libapache2-mod-php ) )

declare -A available_packages

for name in ${package_list[@]} ; do
    available_packages["${name}"]=1
done

for element in ${search_packages[@]} ; do

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
