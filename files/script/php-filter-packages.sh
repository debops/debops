#!/bin/bash

set -o pipefail -o errexit

php_version="${PHP_VERSION:-5}"

search_packages="${@:-}"

package_list=( $(apt-cache --no-generate pkgnames php ) )

declare -A available_packages

for name in ${package_list[@]} ; do
    available_packages["${name}"]=1
done

for element in ${search_packages[@]} ; do

    if [[ ${available_packages["php${php_version}-${element}"]} ]] ; then
        echo "php${php_version}-${element}"
    elif [[ ${available_packages["php-${element}"]} ]] ; then
        echo "php-${element}"
    else
        echo "${element}"
    fi

done
