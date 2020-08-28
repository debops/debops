# -*- mode: ruby -*-
# vi: set ft=ruby :

# Set up an Ansible Controller host with DebOps support using Vagrant
#
# Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017 DebOps project https://debops.org/


# Basic usage:
#
#     vagrant up && vagrant ssh
#     cd src/controller ; debops


# Configuration variables:
#
#     VAGRANT_BOX="debian/buster64"
#         Specify the box to use for controller.
#
#     VAGRANT_NODE_BOX="debian/buster64"
#         Specify the box to use for nodes.
#
#     VAGRANT_NODES=0
#         Specify the number of additional nodes. Default: 0.
#
#     ANSIBLE_FROM="pypi" (default) / ANSIBLE_FROM="debian" / ANSIBLE_FROM="devel"
#         Specify the way to install ansible.
#
#     DEBOPS_FROM="devel" / DEBOPS_FROM="pypi"
#         Specify the way to install debops.
#
#     VAGRANT_HOSTNAME="buster"
#         Set a custom hostname after the box boots up.
#
#     CONTROLLER=false
#         Set to 'true' to set up a configuration with normal Diffie-Hellman
#         parameters (3072, 2048) instead of a smaller one (1024). Initial DH
#         parameter generation may take a long time.
#
#     APT_HTTP_PROXY=""           (http://apt.example.org:3142)
#         Set a custom APT cache URL inside the Vagrant box.
#
#     APT_FORCE_NETWORK="4" / APT_FORCE_NETWORK="6"
#         Configure APT to connect only over IPv4 or IPv6 network. This might
#         be required when connectivity on either network is spotty or broken.


$setup_eatmydata = <<SCRIPT
set -o nounset -o pipefail -o errexit

# Avoid fsync in specific tools to make testing faster.
# We don't care about cleanup, because this is a test VM which will be
# destroyed anyway.
# Ref: http://people.skolelinux.org/pere/blog/Speeding_up_the_Debian_installer_using_eatmydata_and_dpkg_divert.html

apt-get update
apt-get -qy install eatmydata || true
if [ -x "/usr/bin/eatmydata" ] ; then
    for binary in dpkg apt-cache apt-get aptitude tasksel pip pip3 bundle bundler gem npm yarn go rsync ; do
        filename="/usr/bin/${binary}"
        # Test that the file exists and has not been diverted already.
        if [ ! -f "${filename}.distrib" ] ; then
            printf "Diverting %s using eatmydata\n" "${filename}"
            printf "#!/bin/sh\neatmydata $binary.distrib \\"\\$@\\"\n" \
                > "${filename}.vagrant"
            chmod 755 "${filename}.vagrant"
            dpkg-divert --package vagrant \
                --rename --quiet --add "${filename}"
            ln -sf "./${binary}.vagrant" "${filename}"
        else
            printf "Notice: %s is already diverted, skipping\n" "${filename}"
        fi
    done
else
    printf "Error: Unable to find /usr/bin/eatmydata after installing the eatmydata package\n"
fi
SCRIPT

$fix_hostname_dns = <<SCRIPT
set -o nounset -o pipefail -o errexit

current_fqdn="$(hostname --fqdn)"
current_hostname="$(hostname)"

current_default_dev="$(ip route | grep -E '^default via' | awk '{print $5}')"

# In the 'ip route' table, find all of the lines that describe the default
# route based on the device, fint the 'src' field and print out the next field
# which will contain the IP address of the host.
current_default_ip="$(ip route \
                      | grep "dev "${current_default_dev}"" \
                      | grep -v -E '^default via' \
                      | grep src \
                      | awk '{for (I=1;I<=NF;I++) if ($I == "src") {print $(I+1)};}' \
                      | uniq)"

# Fix for https://github.com/hashicorp/vagrant/issues/7263
printf "Updating the box IP address to '%s' in /etc/hosts...\n" "${current_default_ip}"
sed -i -e "/^127\.0\.0\.1.*$(hostname -f | sed -e 's/\./\\\./g')/d" /etc/hosts

# Remove static IP address based on the hostname
sed -i '/^127\.0\.1\.1/d' /etc/hosts

# The upstream Vagrant box image contains 'buster' as an alias of
# 'localhost', let's remove it to avoid potential issues.
sed -i -r -e 's/^127\.0\.0\.1\\s+localhost.*$/127.0.0.1\\tlocalhost/' /etc/hosts

# This provisioning script is executed on all nodes in the cluster,
# the "master" node does not have a suffix to extract.
if printf "${current_hostname}\n" | grep -E '^.*\-.*\-node[0-9]{1,3}$' ; then
    node_short="$(printf "${current_hostname}" | awk -F'-' '{print $3}')"
else
    node_short="master"
fi

# Add an '/etc/hosts' entry for the current host. The rest of the cluster
# will be defined later by the master node.
printf "%s\t%s %s %s\n" "${current_default_ip:-127.0.1.1}" "${current_fqdn}" \
       "${current_hostname}" "${node_short}" >> /etc/hosts

# Install Avahi and configure a custom service to help the master host detct
# other nodes in the cluster. Avahi might be blocked later by the firewall, but
# that is expected; the service is not used for anything in particular beyond
# initial cluster provisioning.
#
mkdir -p "/etc/systemd/system/avahi-daemon.service.d"
cat <<EOF >> "/etc/systemd/system/avahi-daemon.service.d/rlimits-override.conf"
# Override installed by DebOps Vagrantfile
#
# Avoid issues with low nproc limits on LXC hosts with unprivileged LXC
# containers sharing host UIDs/GIDs
# Ref: https://github.com/lxc/lxd/issues/2948
# Ref: https://loune.net/2011/02/avahi-setrlimit-nproc-and-lxc/
[Service]
ExecStart=
ExecStart=/usr/sbin/avahi-daemon -s --no-rlimits
EOF
systemctl daemon-reload
if ! type avahi-daemon > /dev/null ; then
    apt-get -qy install avahi-daemon avahi-utils libnss-mdns
fi

cluster_prefix="$(hostname | sed -e 's/-node.*$//')"

if ! [ -f "/etc/avahi/services/debops-cluster.service" ] ; then
    cat <<EOF > "/etc/avahi/services/debops-cluster.service"
<?xml version="1.0" standalone='no'?><!--*-nxml-*-->
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">%h</name>
  <service>
    <type>_${cluster_prefix}-cluster._tcp</type>
    <port>22</port>
  </service>
</service-group>
EOF
fi

SCRIPT

$provision_box = <<SCRIPT
set -o nounset -o pipefail -o errexit

export JANE_VAGRANT_INCEPTION="true"
readonly PROVISION_CI="#{ENV['CI']}"
readonly PROVISION_GITLAB_CI="#{ENV['GITLAB_CI']}"
readonly PROVISION_VAGRANT_HOSTNAME="#{ENV['VAGRANT_HOSTNAME']}"
readonly PROVISION_APT_HTTP_PROXY="#{ENV['APT_HTTP_PROXY']}"
readonly PROVISION_APT_HTTPS_PROXY="#{ENV['APT_HTTPS_PROXY']}"
readonly PROVISION_APT_FORCE_NETWORK="#{ENV['APT_FORCE_NETWORK']}"
readonly PROVISION_ANSIBLE_FROM="#{ENV['ANSIBLE_FROM'] || 'pypi'}"
readonly PROVISION_DEBOPS_FROM="#{ENV['DEBOPS_FROM'] || 'devel'}"
readonly VAGRANT_PREPARE_BOX="#{ENV['VAGRANT_PREPARE_BOX']}"

# Install the Jane script
if ! type jane > /dev/null 2>&1 ; then
    export JANE_BOX_INIT="true"
    if [ -e "/vagrant/lib/tests/jane" ] ; then
        cp /vagrant/lib/tests/jane /usr/local/bin/jane && chmod +x /usr/local/bin/jane
        jane notify info "Jane installed"
    else
        tee "/usr/local/bin/jane" > "/dev/null" <<EOF
#!/bin/sh

# Fake stub Jane script
printf "%s\\n" "JANE: \\${\*}"
EOF
    chmod +x /usr/local/bin/jane
    fi
else
    if [ -e "/vagrant/lib/tests/jane" ] ; then
        if ! cmp "/vagrant/lib/tests/jane" "/usr/local/bin/jane" ; then
            cp /vagrant/lib/tests/jane /usr/local/bin/jane && chmod +x /usr/local/bin/jane
            jane notify info "Jane updated"
        else
            jane notify ok "Jane up to date"
        fi
    else
        jane notify ok "Jane found at '$(which jane)'"
    fi
fi

# Disable automated APT operations as soon as possible.  This is only valid for
# testing environments and helps avoid errors due to locked APT/dpkg.
# https://unix.stackexchange.com/questions/315502/
if [ -n "${PROVISION_CI}" ] ; then

   jane notify info "Stopping apt-daily.service..."
   systemctl stop apt-daily.service || true
   systemctl kill --kill-who=all apt-daily.service || true
   systemctl stop apt-daily.timer || true

   next_wait_time=0
   until systemctl list-units --all apt-daily.service | fgrep -q dead || [ $next_wait_time -eq 2 ] ; do
       jane notify info "Waiting for apt-daily.service to go down..."
       sleep $(( next_wait_time++ ))
   done

   jane notify info "Stopping apt-daily-upgrade.service..."
   systemctl stop apt-daily-upgrade.service || true
   systemctl kill --kill-who=all apt-daily-upgrade.service || true
   systemctl stop apt-daily-upgrade.timer || true

   next_wait_time=1
   until systemctl list-units --all apt-daily-upgrade.service | fgrep -q dead || [ $next_wait_time -eq 4 ] ; do
       jane notify info "Waiting for apt-daily-upgrade.service to go down..."
       sleep $(( next_wait_time++ ))
   done

   rm -rf /var/lib/systemd/timers/*.timer
fi

# Configure APT proxy
if [ -n "${PROVISION_APT_HTTP_PROXY}" ] ; then
    tee "/etc/apt/apt.conf.d/00aptproxy" > "/dev/null" <<EOF
Acquire::http::Proxy "${PROVISION_APT_HTTP_PROXY}";
Acquire::https::Proxy "false";
EOF
    if [ -n "${PROVISION_APT_HTTPS_PROXY}" ] ; then
        tee -a "/etc/apt/apt.conf.d/00aptproxy" > "/dev/null" <<EOF
Acquire::https::Proxy "${PROVISION_APT_HTTPS_PROXY}";
EOF
    else
        tee -a "/etc/apt/apt.conf.d/00aptproxy" > "/dev/null" <<EOF
Acquire::https::Proxy "DIRECT";
EOF
    fi
fi

# Force IPv4/IPv6 connections in APT depending on the test network requirements
# https://bugs.debian.org/611891
if [ -n "${PROVISION_APT_FORCE_NETWORK}" ] ; then
    if [ "${PROVISION_APT_FORCE_NETWORK}" = "4" ] ; then
        jane notify info "Forcing APT to only use IPv4 network"
        tee -a "/etc/apt/apt.conf.d/00force-ip-network" > "/dev/null" <<EOF
Acquire::ForceIPv4 "true";
EOF
    elif [ "${PROVISION_APT_FORCE_NETWORK}" = "6" ] ; then
        jane notify info "Forcing APT to only use IPv6 network"
        tee -a "/etc/apt/apt.conf.d/00force-ip-network" > "/dev/null" <<EOF
Acquire::ForceIPv6 "true";
EOF
    fi
fi

# Configure GitLab CI environment
if [ -n "${PROVISION_GITLAB_CI}" ] && [ "${PROVISION_GITLAB_CI}" == "true" ] ; then
    tee "/etc/profile.d/vagrant_vars.sh" > "/dev/null" <<EOF
export JANE_INCEPTION="true"
export CI="#{ENV['CI']}"
export GITLAB_CI="#{ENV['GITLAB_CI']}"
export CI_JOB_ID="#{ENV['CI_JOB_ID']}"
export CI_JOB_NAME="#{ENV['CI_JOB_NAME']}"
export CI_JOB_STAGE="#{ENV['CI_JOB_STAGE']}"
export JANE_TEST_PLAY="#{ENV['JANE_TEST_PLAY']}"
export JANE_TEST_FACT="#{ENV['JANE_TEST_FACT']}"
export JANE_TEST_SCRIPT="#{ENV['JANE_TEST_SCRIPT']}"
export JANE_IGNORE_IDEMPOTENCY="#{ENV['JANE_IGNORE_IDEMPOTENCY']}"
export JANE_FORCE_TESTS="#{ENV['JANE_FORCE_TESTS']}"
export JANE_INVENTORY_DIRS="#{ENV['JANE_INVENTORY_DIRS']}"
export JANE_INVENTORY_GROUPS="#{ENV['JANE_INVENTORY_GROUPS']}"
export JANE_INVENTORY_HOSTVARS="#{ENV['JANE_INVENTORY_HOSTVARS']}"
export JANE_KEEP_BOX="#{ENV['JANE_KEEP_BOX']}"
export VAGRANT_BOX="#{ENV['VAGRANT_BOX']}"
export VAGRANT_DOTFILE_PATH="#{ENV['VAGRANT_DOTFILE_PATH']}"
export TERM="#{ENV['TERM']}"
EOF
fi

provision_apt_http_proxy=""
provision_apt_https_proxy=""
eval $(apt-config shell provision_apt_http_proxy Acquire::http::Proxy)
eval $(apt-config shell provision_apt_https_proxy Acquire::https::Proxy)

if [ -n "${provision_apt_http_proxy}" ] ; then
    jane notify config "APT HTTP proxy is enabled: '${provision_apt_http_proxy}'"
fi

if [ -n "${provision_apt_https_proxy}" ] ; then
    if [ "${provision_apt_https_proxy}" == "DIRECT" ] ; then
        jane notify config "APT HTTPS proxy is disabled"
    else
        jane notify config "APT HTTPS proxy is enabled: '${provision_apt_https_proxy}'"
    fi
fi

ansible_from_debian=""
ansible_from_pypi=""
ansible_from_devel=""
if [ "${PROVISION_ANSIBLE_FROM}" == "debian" ] ; then
    ansible_from_debian="ansible"
elif [ "${PROVISION_ANSIBLE_FROM}" == "pypi" ] ; then
    ansible_from_pypi="ansible"
else
    ansible_from_devel="${PROVISION_ANSIBLE_FROM}"
fi

debops_from_pypi=""
debops_from_devel=""
if [ "${PROVISION_DEBOPS_FROM}" == "pypi" ] || ! [ -d "/vagrant" ] ; then
    debops_from_pypi="debops"
else
    debops_from_devel="true"
fi

# Configure Ansible
if ! type ansible > /dev/null 2>&1 && [ ! -f /home/vagrant/.local/bin/ansible ] ; then
    jane notify warning "Ansible not found"

    os_release="$(grep -E '^VERSION=' /etc/os-release | tr -d '(")' | cut -d' ' -f2 | tr -d '\n')"

    tee "/etc/apt/sources.list" > "/dev/null" <<EOF
deb http://deb.debian.org/debian ${os_release} main
deb http://deb.debian.org/debian ${os_release}-updates main
deb http://deb.debian.org/debian ${os_release}-backports main
EOF

    if [ "${os_release}" == "wheezy" ] || [ "${os_release}" == "jessie" ] || [ "${os_release}" == "stretch" ] || [ "${os_release}" == "buster" ] ; then
        tee -a "/etc/apt/sources.list" > "/dev/null" <<EOF
deb http://security.debian.org/ ${os_release}/updates main
EOF
    else
        tee -a "/etc/apt/sources.list" > "/dev/null" <<EOF
deb http://security.debian.org/ ${os_release}-security main
EOF
    fi

    tee "/etc/apt/preferences.d/provision_ansible.pref" > "/dev/null" <<EOF
Package: ansible
Pin: release a=${os_release}-backports
Pin-Priority: 500
EOF

    jane notify cache "Refreshing APT cache"
    apt-get update

    if [ -n "${ansible_from_devel}" ] ; then
        jane notify install "Installing Ansible from GitHub..."
        /vagrant/ansible/roles/debops.ansible/files/script/bootstrap-ansible "${ansible_from_devel}"
    fi

    jane notify install "Installing Ansible requirements via APT..."
    DEBIAN_FRONTEND=noninteractive apt-get -y \
    --no-install-recommends install \
        acl \
        apt-transport-https \
        git \
        haveged \
        jo \
        jq \
        make \
        python-apt \
        python-distro \
        python-dnspython \
        python-future \
        python-jinja2 \
        python-ldap \
        python-netaddr \
        python-nose2 \
        python-nose2-cov \
        python-openssl \
        python-passlib \
        python-pip \
        python-pycodestyle \
        python-pytest \
        python-pytest-cov \
        python-setuptools \
        python-sphinx \
        python-sphinx-rtd-theme \
        python-unittest2 \
        python-wheel \
        python-yaml \
        python3 \
        python3-apt \
        python3-distro \
        python3-dnspython \
        python3-future \
        python3-jinja2 \
        python3-netaddr \
        python3-nose2 \
        python3-nose2-cov \
        python3-openssl \
        python3-passlib \
        python3-pip \
        python3-pycodestyle \
        python3-pytest \
        python3-pytest-cov \
        python3-setuptools \
        python3-sphinx \
        python3-sphinx-rtd-theme \
        python3-unittest2 \
        python3-wheel \
        python3-yaml \
        rsync \
        shellcheck \
        yamllint

    # Install packages needed to build missing Python modules
    if [ "${os_release}" == "wheezy" ] || [ "${os_release}" == "jessie" ] || [ "${os_release}" == "stretch" ] ; then

        DEBIAN_FRONTEND=noninteractive apt-get -y \
        --no-install-recommends install \
            build-essential \
            libffi-dev \
            libldap2-dev \
            libsasl2-dev \
            libssl-dev \
            python-dev \
            python3-dev
    fi

    if [ ! "${os_release}" == "wheezy" ] && [ ! "${os_release}" == "jessie" ] && [ ! "${os_release}" == "stretch" ] ; then

        DEBIAN_FRONTEND=noninteractive apt-get -y \
        --no-install-recommends install \
            python3-ldap
    fi

    DEBIAN_FRONTEND=noninteractive apt-get -y \
    --no-install-recommends install ${ansible_from_debian}

    jane notify cache "Cleaning up cache directories..."
    find /var/lib/apt/lists -maxdepth 1 -type f ! -name 'lock' -delete
    find /var/cache/apt/archives -maxdepth 1 -name '*.deb' -delete
    rm -rf /root/.cache/* /tmp/*
fi

# Update APT cache on the first boot after provisioning so that APT packages
# can be installed correctly right away.
if [ -z "${JANE_BOX_INIT:-}" ] ; then
    jane notify cache "Refreshing APT cache"
    apt-get update
fi

if [ -n "${VAGRANT_PREPARE_BOX}" ] ; then
    jane notify info "Removing host entry from '/etc/hosts' for CI environment"
    sed -i -e "/$(hostname --fqdn)/d" /etc/hosts

    jane notify info "Removing machine-id information for CI environment"
    rm -f /var/lib/dbus/machine-id
    truncate -s 0 /etc/machine-id

    jane notify info "Removing random seed for CI environment"
    systemctl stop systemd-random-seed
    rm -f /var/lib/systemd/random-seed
fi

jane notify success "Vagrant box provisioning complete"
SCRIPT

$provision_node_box = <<SCRIPT
set -o nounset -o pipefail -o errexit

JANE_VAGRANT_INCEPTION="true"
PROVISION_GITLAB_CI="#{ENV['GITLAB_CI']}"
PROVISION_APT_HTTP_PROXY="#{ENV['APT_HTTP_PROXY']}"
PROVISION_APT_HTTPS_PROXY="#{ENV['APT_HTTPS_PROXY']}"
PROVISION_APT_FORCE_NETWORK="#{ENV['APT_FORCE_NETWORK']}"

# Configure GitLab CI environment
if [ -n "${PROVISION_GITLAB_CI}" ] && [ "${PROVISION_GITLAB_CI}" == "true" ] ; then
    tee "/etc/profile.d/vagrant_vars.sh" > "/dev/null" <<EOF
export JANE_INCEPTION="true"
export CI="#{ENV['CI']}"
export GITLAB_CI="#{ENV['GITLAB_CI']}"
export CI_JOB_ID="#{ENV['CI_JOB_ID']}"
export TERM="#{ENV['TERM']}"
EOF
fi

# Install the CI supervisor script
if ! type jane > /dev/null 2>&1 ; then
    if [ -e "/vagrant/lib/tests/jane" ] ; then
        cp /vagrant/lib/tests/jane /usr/local/bin/jane && chmod +x /usr/local/bin/jane
        jane notify info "Jane installed"
    else
        tee "/usr/local/bin/jane" > "/dev/null" <<EOF
#!/bin/sh

# Fake Jane script
printf "%s\\n" "JANE: \\${*}"
EOF
    chmod +x /usr/local/bin/jane
    fi
else
    jane notify ok "Jane found at '$(which jane)'"

    jane notify info "Refreshing APT sources"
    apt-get -qq update
fi

# Configure APT cache
if [ -n "${PROVISION_APT_HTTP_PROXY}" ] ; then
    jane notify info "Configuring APT cache at '${PROVISION_APT_HTTP_PROXY}'"
    cat "/etc/apt/apt.conf.d/00aptproxy" <<EOF
Acquire::http::Proxy "${PROVISION_APT_HTTP_PROXY}";
EOF
fi

# Force IPv4/IPv6 connections in APT depending on the test network requirements
# https://bugs.debian.org/611891
if [ -n "${PROVISION_APT_FORCE_NETWORK}" ] ; then
    if [ "${PROVISION_APT_FORCE_NETWORK}" = "4" ] ; then
        jane notify info "Forcing APT to only use IPv4 network"
        cat "/etc/apt/apt.conf.d/00force-ip-network" <<EOF
Acquire::ForceIPv4 "true";
EOF
    elif [ "${PROVISION_APT_FORCE_NETWORK}" = "6" ] ; then
        jane notify info "Forcing APT to only use IPv6 network"
        cat "/etc/apt/apt.conf.d/00force-ip-network" <<EOF
Acquire::ForceIPv6 "true";
EOF
    fi
fi

jane notify info "Vagrant node provisioning complete"
SCRIPT

$provision_ansible = <<SCRIPT
set -o nounset -o pipefail -o errexit

readonly PROVISION_ANSIBLE_FROM="#{ENV['ANSIBLE_FROM'] || 'pypi'}"
readonly PROVISION_DEBOPS_FROM="#{ENV['DEBOPS_FROM'] || 'devel'}"

if ! type ansible > /dev/null 2>&1 ; then
    jane notify warning "Ansible not found"

    jane notify info "Provisioning Ansible ..."

    # Ensure that the Ansible Controller host has up to date APT cache to be able
    # to install the packages without friction.
    sudo apt-get -q update

    ansible_from_pypi=""
    if [ "${PROVISION_ANSIBLE_FROM}" == "pypi" ] ; then
        ansible_from_pypi="ansible"
    fi

    debops_from_pypi=""
    debops_from_devel=""
    if [ "${PROVISION_DEBOPS_FROM}" == "pypi" ] || ! [ -d "/vagrant" ] ; then
        debops_from_pypi="debops"
    else
        debops_from_devel="true"
    fi

    # Use Python 2.7 environment on older OS releases
    os_release="$(grep -E '^VERSION=' /etc/os-release | tr -d '(")' | cut -d' ' -f2 | tr -d '\n')"
    if [ "${os_release}" == "wheezy" ] || [ "${os_release}" == "jessie" ] || [ "${os_release}" == "stretch" ] ; then
        pipwrap="pip"
    else
        pipwrap="pip3"
    fi
    jane notify install "Installing Ansible requirements via PyPI using ${pipwrap}..."

    "${pipwrap}" install --user netaddr python-ldap dnspython passlib future testinfra ${ansible_from_pypi} ${debops_from_pypi}

    if [ -n "${debops_from_devel}" ] ; then
        mkdir /tmp/build
        rsync -a --exclude '.vagrant' /vagrant/ /tmp/build
        cd /tmp/build
        make sdist-quiet > /dev/null
        "${pipwrap}" install --user dist/*
        cd - > /dev/null
    fi

    # Add ~/.local/bin to PATH on older OS releases
    if ! grep -q "HOME/.local/bin" ~/.profile ; then
        cat << EOF >> "${HOME}/.profile"

# set PATH so it includes user's private bin if it exists
if [ -d "\\$HOME/.local/bin" ] ; then
    PATH="\\$HOME/.local/bin:\\$PATH"
fi
EOF
    fi

    jane notify cache "Cleaning up cache directories..."
    rm -rf ~/.cache/*
    sudo rm -rf /root/.cache/* /tmp/*

    jane notify info "Ansible provisioning complete"
else
    jane notify ok "Ansible found at '$(which ansible)'"
    ansible --version
fi
SCRIPT

$provision_controller = <<SCRIPT
set -o nounset -o pipefail -o errexit

readonly PROVISION_ANSIBLE_FROM="#{ENV['ANSIBLE_FROM'] || 'pypi'}"
readonly PROVISION_DEBOPS_FROM="#{ENV['DEBOPS_FROM'] || 'devel'}"

jane notify info "Configuring Ansible Controller host..."

# Ensure that the Ansible Controller host has up to date APT cache to be able
# to install the packages without friction.
sudo apt-get -q update

ansible_from_pypi=""
if [ "${PROVISION_ANSIBLE_FROM}" == "pypi" ] ; then
    ansible_from_pypi="ansible"
fi

debops_from_pypi=""
debops_from_devel=""
if [ "${PROVISION_DEBOPS_FROM}" == "pypi" ] || ! [ -d "/vagrant" ] ; then
    debops_from_pypi="debops"
else
    debops_from_devel="true"
fi

jane notify install "Installing requirements via PyPI..."

pip3 install --user netaddr python-ldap dnspython passlib future testinfra ${ansible_from_pypi} ${debops_from_pypi}

if [ -n "${debops_from_devel}" ] ; then
    mkdir /tmp/build
    rsync -a --exclude '.vagrant' /vagrant/ /tmp/build
    cd /tmp/build
    make sdist-quiet > /dev/null
    pip3 install --user dist/*
    cd - > /dev/null
fi

jane notify cache "Cleaning up cache directories..."
rm -rf ~/.cache/*
sudo rm -rf /root/.cache/* /tmp/*

if ! [ -e .local/share/debops/debops ] ; then
    mkdir -p src .local/share/debops
    if [ -n "${debops_from_devel}" ] ; then
        jane notify info "Symlinking '/vagrant' to '~vagrant/.local/share/debops/debops'"
        ln -s /vagrant .local/share/debops/debops
    else
        jane notify info "Installing DebOps monorepo to '~vagrant/.local/share/debops/debops'"
        debops-update
    fi
fi

if ! [ -d src/controller ] ; then
    debops-init src/controller
    sed -i '/ansible_connection=local$/ s/^#//' src/controller/ansible/inventory/hosts

    vagrant_controller="$(printf "${SSH_CLIENT}\\n" | awk '{print $1}')"
    mkdir -p "src/controller/ansible/inventory/group_vars/all"
    mkdir -p "src/controller/ansible/inventory/host_vars/$(hostname)"
    cat <<EOF >> "src/controller/ansible/inventory/group_vars/all/dhparam.yml"
---

# Use smaller Diffie-Hellman parameters to speed up test runs
dhparam__bits: [ '1024' ]
EOF
    cat <<EOF >> "src/controller/ansible/inventory/group_vars/all/core.yml"
---

# Vagrant client detected from \\$SSH_CLIENT variable
core__ansible_controllers: [ '${vagrant_controller}' ]
EOF
    # Provide an 'alias' for the master host in Ansible inventory, for
    # convenience and parity with an alias in the '/etc/hosts database.
    cat <<EOF >> "src/controller/ansible/inventory/master"
# DebOps master node
[master]
$(hostname)
EOF
    # Create the 'nodes' Ansible inventory group for all remote cluster nodes.
    cat <<EOF >> "src/controller/ansible/inventory/nodes"
# All DebOps test nodes in the inventory
[nodes]
EOF
    cluster_nodes=( $(avahi-browse _$(hostname)-cluster._tcp -pt \
                    | awk -F';' '{print $4}' | sort | uniq | xargs) )

    for node in ${cluster_nodes[@]} ; do

       if printf "${node}\\n" | grep -E '^.*\-.*\-node[0-9]{1,3}$' > /dev/null ; then
            node_short="$(printf "${node}\\n" | awk -F'-' '{print $3}')"
            node_pad=" "
        else
            node_short=""
            node_pad=""
        fi

        if ! grep "${node}.$(dnsdomainname)" /etc/hosts > /dev/null ; then
            jane notify info "Creating ${node}.$(dnsdomainname) host record"
            printf "%s\t%s %s%s%s\n" "$(getent hosts ${node}.local | awk '{print $1'})" \
                   "${node}.$(dnsdomainname)" "${node}" "${node_pad}" "${node_short}" \
                   | sudo tee --append /etc/hosts

            jane notify info "Adding ${node}.$(dnsdomainname) to Ansible inventory"
            printf "%s ansible_host=%s\n" "${node}" "${node}.$(dnsdomainname)" \
                   >> src/controller/ansible/inventory/hosts

            # Scan the SSH host fingerprints of the detected nodes based on
            # their DNS records. This is done for Ansible usage as well as to
            # allow creation of the DNS records on remote nodes.
            ssh-keyscan -H "${node}.$(dnsdomainname)" >> ~/.ssh/known_hosts 2>/dev/null
            ssh-keyscan -H "${node_short}" >> ~/.ssh/known_hosts 2>/dev/null
            ssh-keyscan -H "${node}" >> ~/.ssh/known_hosts 2>/dev/null

            # Add the detected node to the 'nodes' Ansible inventory group.
            printf "%s\n" "${node}" >> "src/controller/ansible/inventory/nodes"
            if [ -n "${node_short}" ] ; then

                # Create an 'alias' in the Ansible inventory for a given node,
                # for convenience and parity with an alise in the '/etc/hosts'
                # database.
                cat <<EOF >> "src/controller/ansible/inventory/${node_short}"
[${node_short}]
${node}
EOF
            fi

            # Connect to each detected node and use Avahi to discover other
            # nodes in the cluster and create host entries in the '/etc/hosts'
            # database on the remote nodes.
            # This does not work during initial '/etc/hosts' configuration and
            # has to be done from the master node.
            ssh "${node}.$(dnsdomainname)" <<'SSHEND' > /dev/null 2>&1
cluster_nodes=( $(avahi-browse _$(hostname | sed -e 's/\\-node[0-9]\\{1,3\\}$//')-cluster._tcp -pt \
                | awk -F';' '{print $4}' | sort | uniq | xargs) )
for node in ${cluster_nodes[@]} ; do
    if printf "${node}\n" | grep -E '^.*\-.*\\-node[0-9]{1,3}$' ; then
        node_short="$(printf "${node}\\n" | awk -F'-' '{print $3}')"
    else
        node_short="master"
    fi
    if ! grep "${node}.$(dnsdomainname)" /etc/hosts > /dev/null ; then
        printf "Creating %s host record\\n" "${node}.$(dnsdomainname)"
        printf "%s\\t%s %s %s\\n" "$(getent hosts ${node}.local | awk '{print $1'})" \
               "${node}.$(dnsdomainname)" "${node}" "${node_short}" \
               | sudo tee --append /etc/hosts > /dev/null
    fi
done
SSHEND
        fi
    done
fi

jane notify info "Ansible Controller provisioning complete"
SCRIPT

require 'securerandom'

VAGRANT_DOMAIN = ENV['VAGRANT_DOMAIN'] || 'vagrant.test'
VAGRANT_HOSTNAME_MASTER = (ENV['VAGRANT_DOTFILE_PATH'] || '.vagrant') + '/vagrant_hostname_master'
if File.exist? VAGRANT_HOSTNAME_MASTER
      master_hostname = IO.read( VAGRANT_HOSTNAME_MASTER ).strip
else
      master_hostname = ENV['VAGRANT_HOSTNAME'] || "debops-#{SecureRandom.hex(3)}"
      IO.write( VAGRANT_HOSTNAME_MASTER, master_hostname )
end
master_fqdn = master_hostname + '.' + VAGRANT_DOMAIN

# Persist the number of additional nodes in the DebOps cluster to allow
# 'vagrant' commands without the VAGRANT_NODES variable being set in the
# environment.
VAGRANT_NODE_NUMBER = (ENV['VAGRANT_DOTFILE_PATH'] || '.vagrant') + '/vagrant_node_number'
if File.exist? VAGRANT_NODE_NUMBER
    VAGRANT_NODES = ENV['VAGRANT_NODES'] || IO.read( VAGRANT_NODE_NUMBER ).strip
else
    VAGRANT_NODES = ENV['VAGRANT_NODES'] || 0
end
IO.write( VAGRANT_NODE_NUMBER, VAGRANT_NODES )

# Randomize forwarded SSH port to avoid clashes with multiple Vagrant instances
# started at the same time
r = Random.new
VAGRANT_SSH_PORT_MASTER = (ENV['VAGRANT_DOTFILE_PATH'] || '.vagrant') + '/vagrant_ssh_port_master'
if File.exist? VAGRANT_SSH_PORT_MASTER
    master_ssh_port = IO.read( VAGRANT_SSH_PORT_MASTER ).strip
else
    master_ssh_port = r.rand(2300..2800)
    IO.write( VAGRANT_SSH_PORT_MASTER, master_ssh_port )
end
master_fqdn = master_hostname + '.' + VAGRANT_DOMAIN

VAGRANT_NODE_BOX = ENV['VAGRANT_NODE_BOX'] || 'debian/buster64'

# Vagrant removed the atlas.hashicorp.com to vagrantcloud.com
# redirect. The value of DEFAULT_SERVER_URL in Vagrant versions
# less than 1.9.3 is atlas.hashicorp.com. This breaks the fetching
# and updating of boxes as they are now stored in
# vagrantcloud.com instead of atlas.hashicorp.com.
# https://github.com/hashicorp/vagrant/issues/9442
if Vagrant::DEFAULT_SERVER_URL.include?('atlas.hashicorp.com')
    Vagrant::DEFAULT_SERVER_URL.replace('https://vagrantcloud.com')
end

Vagrant.configure("2") do |config|

    # Create and provision additional nodes first, so that the master node has
    # time to do provisioning and cluster detection using Avahi later.
    if VAGRANT_NODES != 0
        (1..VAGRANT_NODES.to_i).each do |i|

            node_fqdn = master_hostname + "-node#{i}." + VAGRANT_DOMAIN
            config.vm.define "node#{i}", autostart: true do |node|

                node.vm.box = VAGRANT_NODE_BOX
                node.vm.hostname = node_fqdn
                node.vm.provision "shell", inline: $setup_eatmydata,    keep_color: true
                node.vm.provision "shell", inline: $fix_hostname_dns,   keep_color: true
                node.vm.provision "shell", inline: $provision_node_box, keep_color: true, run: "always"

                # Don't populate '/vagrant' directory on other nodes
                node.vm.synced_folder ".", "/vagrant", disabled: true

                if ENV['VAGRANT_BOX'] || 'debian/buster64' == 'debian/buster64'
                    node.ssh.insert_key = false
                end

                node.vm.provider "libvirt" do |libvirt|
                    libvirt.random_hostname = true
                    libvirt.memory = ENV['VAGRANT_NODE_MEMORY'] || '512'
                    libvirt.cpus   = ENV['VAGRANT_NODE_CPUS']   || '2'

                    if ENV['GITLAB_CI'] != "true"
                        libvirt.memory = ENV['VAGRANT_NODE_MEMORY'] || '1024'
                    end
                end

                node.vm.provider "virtualbox" do |virtualbox, override|
                    override.vm.network "private_network", type: "dhcp"
                end
            end
        end
    end

    config.vm.define "master", primary: true do |subconfig|
        subconfig.vm.box = ENV['VAGRANT_BOX'] || 'debian/buster64'
        subconfig.vm.hostname = master_fqdn

        subconfig.vm.network "forwarded_port", guest: 22, host: "#{master_ssh_port}", id: 'ssh', auto_correct: true

        # Vagrant should generate a random MAC address for a box
        subconfig.vm.base_mac = nil

        subconfig.vm.provision "shell", inline: $setup_eatmydata,  keep_color: true
        subconfig.vm.provision "shell", inline: $fix_hostname_dns, keep_color: true
        subconfig.vm.provision "shell", inline: $provision_box,    keep_color: true, run: "always"
        subconfig.vm.provision "shell", inline: $provision_ansible, keep_color: true, privileged: false

        # Inject the insecure Vagrant SSH key into the master node so it can be
        # used by Ansible and cluster detection to connect to the other nodes.
        subconfig.vm.provision "file", source: "#{Dir.home}/.vagrant.d/insecure_private_key", \
                                       destination: "/home/vagrant/.ssh/id_rsa"
        subconfig.vm.provision "shell" do |s|
            s.inline = <<-SHELL
                chown vagrant:vagrant /home/vagrant/.ssh/id_rsa
                chmod 600 /home/vagrant/.ssh/id_rsa
            SHELL
        end

        if ENV['VAGRANT_BOX'] || 'debian/buster64' == 'debian/buster64'
            subconfig.ssh.insert_key = false
        end

        subconfig.vm.provider "libvirt" do |libvirt, override|
            # On a libvirt provider, default sync method is NFS. If we switch
            # it to 'rsync', this will drop the dependency on NFS on the host.
            override.vm.synced_folder ENV['CI_PROJECT_DIR'] || ".", "/vagrant", type: "rsync", \
                                      rsync__exclude: ['.git/', 'build/', 'docs/', '*.box' ]

            libvirt.random_hostname = true
            libvirt.memory = ENV['VAGRANT_MASTER_MEMORY'] || '1024'
            libvirt.cpus =   ENV['VAGRANT_MASTER_CPUS']   || '2'

            if ENV['GITLAB_CI'] != "true"
                libvirt.memory = ENV['VAGRANT_MASTER_MEMORY'] || '2048'
                libvirt.cpus =   ENV['VAGRANT_MASTER_CPUS']   || '4'
            end
        end

        subconfig.vm.provider "virtualbox" do |virtualbox, override|
            override.vm.network "private_network", type: "dhcp"
        end

        if Vagrant::Util::Platform.windows? then
            # MS Windows doesn't support symlinks, so disable directory sync under it.
            # DebOps will be installed normally, via 'debops-update'
            subconfig.vm.synced_folder ".", "/vagrant", disabled: true
        elsif ENV['GITLAB_CI'] == "true"
            # We are running in a GitLab CI environment
            subconfig.vm.synced_folder ENV['CI_PROJECT_DIR'] || ".", "/vagrant"
        else
            subconfig.vm.synced_folder ENV['PROJECT_DIR'] || ".", "/vagrant"
        end

        if ENV['GITLAB_CI'] != "true"
            subconfig.vm.provision "shell", inline: $provision_controller, keep_color: true, privileged: false
        end

        if ENV['CI'] != "true"
            subconfig.vm.post_up_message = "Thanks for trying DebOps! After logging in, run:
            cd src/controller ; debops common --diff"
        end
    end

end
