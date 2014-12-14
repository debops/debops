#!/bin/bash

# backup-debops.org.sh: small shell script that clones all git
# repositories of the DebOps project and additional tools
#
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


# This script clones all repositories of the DebOps project from GitHub plus
# some additional tools and preserves the '.git' directories.
#
# Various tools will be cloned into 'tools/' directory.
# Ansible roles will be cloned into 'roles/' directory.
#
# Before this script will do git repository backups, you will need to import
# a GPG key used to sign file with list of repositories downloaded from GitHub,
# on the account that will run the script (don't use 'root' account for this!).
#
#    gpg --recv-keys '955CA868949DF13B6375851898BC72D3E3B451EA'
#
# Usage:
#
#    ./backup-debops.org.sh [directory] [mode]
#
# Usage via cron:
#
#    0 3 * * * /home/user/backup-debops.org.sh /home/user/backups > /dev/null


set -e


# ---- Variables ----

# Enable debugging with DEBUG=1
[ -z "${DEBUG}" ] && DEBUG="0"

# Directory where backups should be stored, defaults to current directory
backup_dir="${1:-$PWD}"

# Mode of operation:
# - mirror   = git clone --mirror all repositories (bare)
# - backup   = git clone all repositories
# - restore  = restore from local bare repositories into restore/ subdirectory
mode=${2:-mirror}

# Create the specified directory if it doesn't exist
[ ! -d ${backup_dir} ] && mkdir -p ${backup_dir}

# Absolute path to backup dir
backup_root_dir="$(readlink -f ${backup_dir})"

# Default git URI to use; using 'git://' prefix is 3x faster than 'https://',
# but you go over plaintext
git_github_uri="https://github.com/"

# Default directories in which tools and roles will be split into; you can
# change this to "." to have them all in current directory
debops_tools_dir="tools"
debops_roles_dir="roles"

# Current list of repositories to back up, GPG-signed and downloaded from
# GitHub main project repository
debops_backup_data_uri="https://raw.githubusercontent.com/debops/debops/master/misc/backup"
debops_backup_data_file="backup-data.txt"
debops_backup_data_signature="backup-data.txt.sig"
debops_backup_data_fingerprint="955CA868949DF13B6375851898BC72D3E3B451EA"


# ---- Functions ----

# Verify GPG signature of a file (GPG key needs to be present in the keyring)
verify_signature() {
  local file="${1}"
  local fingerprint="${2}"
  local out=""
  if out=$(gpg --status-fd 1 --verify "${file}" 2>/dev/null) &&
    echo "${out}" | grep -qs "^\[GNUPG:\] VALIDSIG ${fingerprint} " ; then
    return 0
  else
    echo "$out" >&2
    return 1
  fi
}

# Download current list of repositories and verify its GPG signature
download_backup_data () {
  dest_dir="${1}"
  curl --silent ${debops_backup_data_uri}/${debops_backup_data_file} > ${dest_dir}/${debops_backup_data_file}
  curl --silent ${debops_backup_data_uri}/${debops_backup_data_signature} > ${dest_dir}/${debops_backup_data_signature}
  verify_signature ${dest_dir}/${debops_backup_data_signature} ${debops_backup_data_fingerprint} || exit 1
}

# Mirror specified git repository or update
do_git_mirror () {
  local source_path="${1}"
  local destination_path="${2}"

  if [ $DEBUG -gt 0 ] ; then
    echo git clone --mirror ${source_path} ${destination_path}
  else
    if [ ! -d ${destination_path} ]; then
      git clone --mirror ${source_path} ${destination_path}
    else
      pushd ${destination_path} > /dev/null
      git fetch -a
      popd > /dev/null
    fi
  fi
}

# Clone specified git repository or update
do_git_clone () {
  local source_path="${1}"
  local destination_path="${2}"

  if [ $DEBUG -gt 0 ] ; then
    echo git clone ${source_path} ${destination_path}
  else
    if [ ! -d ${destination_path} ]; then
      git clone ${source_path} ${destination_path}
    else
      pushd ${destination_path} > /dev/null
      git pull
      popd > /dev/null
    fi
  fi
}

# Mirror all repositories
git_clone_mirror () {
  clone_destination="${1}" ; shift
  git_uri="${1}" ; shift
  list_of_repositories=("${@}")

  for repository in ${list_of_repositories[@]} ; do

    do_git_mirror "${git_uri}${repository}" "${clone_destination}/${repository}"

  done
}

# Clone all tools without changing their repository name
git_clone_tools () {
  clone_destination="${1}" ; shift
  git_uri="${1}" ; shift
  list_of_repositories=("${@}")

  for repository in ${list_of_repositories[@]} ; do
    repo_name=${repository%.git}

    do_git_clone "${git_uri}${repository}" "${clone_destination}/${repo_name}"

  done
}

# Restore all tools repositories from mirror
git_restore_tools () {
  clone_source="${1}" ; shift
  clone_destination="${1}" ; shift
  list_of_repositories=("${@}")

  for repository in ${list_of_repositories[@]} ; do
    repo_name=${repository%.git}

    do_git_clone "${clone_source}/${repository}" "${clone_destination}/${repo_name}"

  done
}

# Clone all Ansible roles and change their name to format used by Ansible Galaxy
git_clone_roles () {
  clone_destination="${1}" ; shift
  git_uri="${1}" ; shift
  list_of_repositories=("${@}")

  prefix="debops."

  for repository in ${list_of_repositories[@]} ; do
    cut_ansible_role_prefix=${repository#*ansible-role-}
    cut_ansible_prefix=${cut_ansible_role_prefix#*ansible-}
    cut_final=${cut_ansible_prefix%.git}

    repo_name="debops/${prefix}${cut_final}"

    do_git_clone "${git_uri}${repository}" "${clone_destination}/${repo_name}"

  done
}

# Restore all role repositories from mirror
git_restore_roles () {
  clone_source="${1}" ; shift
  clone_destination="${1}" ; shift
  list_of_repositories=("${@}")

  prefix="debops."

  for repository in ${list_of_repositories[@]} ; do
    cut_ansible_role_prefix=${repository#*ansible-role-}
    cut_ansible_prefix=${cut_ansible_role_prefix#*ansible-}
    cut_final=${cut_ansible_prefix%.git}

    repo_name="debops/${prefix}${cut_final}"

    do_git_clone "${clone_source}/${repository}" "${clone_destination}/${repo_name}"

  done
}


# ---- Main script ----

# Check if required commands are present
for name in curl git ; do
  if ! type ${name} > /dev/null 2>&1 ; then
    echo >&2 "$(basename ${0}): Error: ${name}: command not found" ; exit 1
  fi
done

# Lock file to prevent race condition during long backup runs from cron
lockfile="/var/lock/$(basename ${0}).lock"

(
  flock -x -w 0 200 || exit 1

  # Create temporary directory for backup-data.txt
  temp_dir="$(mktemp -d)"

  # Clean up after the script is finished
  trap "rm -rf ${temp_dir} ${lockfile}" EXIT

  # Download current list of git repositories from GitHub and load it
  download_backup_data ${temp_dir}
  source ${temp_dir}/${debops_backup_data_file}

  # Backup all DebOps tools in 'tools/' subdirectory
  if [ -n "${debops_github_tools}" ] ; then
    if [[ "${mode}" == "mirror" ]] ; then
      git_clone_mirror "${backup_root_dir}/debops.org/mirror/${debops_tools_dir}/github.com" "${git_github_uri}" "${debops_github_tools[@]}"
    elif [[ "${mode}" == "backup" ]] ; then
      git_clone_tools "${backup_root_dir}/debops.org/backup/${debops_tools_dir}/github.com" "${git_github_uri}" "${debops_github_tools[@]}"
    elif [[ "${mode}" == "restore" ]] ; then
      git_restore_tools "${backup_root_dir}/debops.org/mirror/${debops_tools_dir}/github.com" "${backup_root_dir}/debops.org/restore/${debops_tools_dir}/github.com" "${debops_github_tools[@]}"
    fi
  fi

  # Clone all DebOps Ansible roles in 'roles/' directory; if you want not
  # modified remository names, change the function name from "_roles" to "_tools"
  if [ -n "${debops_github_roles}" ] ; then
    if [[ "${mode}" == "mirror" ]] ; then
      git_clone_mirror "${backup_root_dir}/debops.org/mirror/${debops_roles_dir}/github.com" "${git_github_uri}" "${debops_github_roles[@]}"
    elif [[ "${mode}" == "backup" ]] ; then
      git_clone_roles "${backup_root_dir}/debops.org/backup/${debops_roles_dir}/github.com" "${git_github_uri}" "${debops_github_roles[@]}"
    elif [[ "${mode}" == "restore" ]] ; then
      git_restore_roles "${backup_root_dir}/debops.org/mirror/${debops_roles_dir}/github.com" "${backup_root_dir}/debops.org/restore/${debops_roles_dir}/github.com" "${debops_github_roles[@]}"
    fi
  fi

) 200>${lockfile}

