#!/bin/sh

# (C) 2015 Maciej Delmanowski <drybjed@gmail.com>
# Homepage: http://debops.org/
# License: GPLv3

# Push GitHub test hooks to Travis-CI on all DebOps roles that have them
# configured, to test all of them at once.


# =========================================================================
# This script needs 'jq' JSON processor from https://stedolan.github.io/jq/
# =========================================================================


# Path to file with GitHub API token
[ -z "${TOKEN}" ] && TOKEN=~/.debops-github-token

if [ -f ${TOKEN} ] ; then
  GITHUB_TOKEN=$(cat ${TOKEN})
else
  echo "No GitHub API token in ${TOKEN} found, exiting"
  exit 1
fi


# URL to list of Ansible roles in ansible-galaxy format
DEBOPS_ROLES_URI="https://raw.githubusercontent.com/debops/debops-playbooks/master/galaxy/requirements.txt"

# Get list of Ansible roles and convert Galaxy names into git repository names
# FIXME: Convert to paginated GitHub API call that gets all repositories of an
# organization
get_debops_roles () {
  if [ -n "${DEBOPS_ROLES_URI}" ] ; then
    curl -s ${DEBOPS_ROLES_URI} | sed -e 's/^debops\./ansible-/' -e 's/ansible\-ansible/ansible-role-ansible/'
  fi
}


# Get Travis-CI hook id from GitHub API
get_travis_hook () {
  local repository="${1}"

  curl -s -u ${GITHUB_TOKEN}:x-oauth-basic https://api.github.com/repos/debops/${repository}/hooks | jq '.[] | select(.name=="travis") | .id'
}

# Push test hook to Travis-CI via GitHub API
post_travis_hook () {
  local repository="${1}"
  local id="${2}"

  curl -u ${GITHUB_TOKEN}:x-oauth-basic -XPOST https://api.github.com/repos/debops/${repository}/hooks/${id}/tests
}


# ---- Main script ----

roles=$(get_debops_roles)

for role in ${roles} ; do

  travis_hook_id=$(get_travis_hook $role)

  if [ -n "${travis_hook_id}" ] ; then

    echo "Pushing Travis-CI button for debops/${role}"
    post_travis_hook ${role} ${travis_hook_id}

  fi

done

