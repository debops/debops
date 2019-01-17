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
#     VAGRANT_BOX="debian/stretch64"
#         Specify the box to use.
#
#     VAGRANT_HOSTNAME="stretch"
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


$provision_box = <<SCRIPT
set -o nounset -o pipefail -o errexit

export JANE_VAGRANT_INCEPTION="true"
readonly PROVISION_CI="#{ENV['CI']}"
readonly PROVISION_GITLAB_CI="#{ENV['GITLAB_CI']}"
readonly PROVISION_VAGRANT_HOSTNAME="#{ENV['VAGRANT_HOSTNAME']}"
readonly PROVISION_APT_HTTP_PROXY="#{ENV['APT_HTTP_PROXY']}"
readonly PROVISION_APT_HTTPS_PROXY="#{ENV['APT_HTTPS_PROXY']}"
readonly PROVISION_APT_FORCE_NETWORK="#{ENV['APT_FORCE_NETWORK']}"
readonly PROVISION_ANSIBLE_FROM="#{ENV['ANSIBLE_FROM'] || 'debian'}"

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

# Configure hostname and domain
REAL_HOSTNAME=""
if [ -n "${PROVISION_VAGRANT_HOSTNAME}" ] ; then
    export REAL_HOSTNAME="${PROVISION_VAGRANT_HOSTNAME}"
elif [ -n "${PROVISION_GITLAB_CI}" ] && [ "${PROVISION_GITLAB_CI}" == "true" ] ; then
    export REAL_HOSTNAME="ci-$(cat /proc/sys/kernel/random/uuid)"
fi

if [ -n "${REAL_HOSTNAME}" ] ; then
    current_fqdn="$(dnsdomainname -A)"
    jane notify info "Changing box hostname to '${REAL_HOSTNAME}'..."
    if [ -d /run/systemd/system ] ; then
        hostnamectl set-hostname "${REAL_HOSTNAME}"
        if [ "$(systemctl is-active systemd-networkd.service)" == "active" ] ; then
            jane notify info "Requesting restart of 'systemd-networkd.service'"
            systemctl restart systemd-networkd.service
        else
            jane notify info "Requesting restart of 'networking.service'..."
            systemctl restart networking.service
        fi
    else
        hostname "${REAL_HOSTNAME}"
        printf "%s\n" "${REAL_HOSTNAME}" > /etc/hostname
        jane notify info "Requesting restart of 'networking' service..."
        /etc/init.d/networking restart
    fi
    jane notify info "Waiting for network configuration to settle..."
    loop_timeout=5
    sleep 2
    until [ "$(dnsdomainname -A)" != "${current_fqdn}" ] || [ ${loop_timeout} -eq 7 ] ; do
        jane notify info "Waiting for new FQDNs..."
        sleep $(( loop_timeout++ ))
    done
    if [ -z "$(dnsdomainname)" ] ; then
        jane notify warning "DNS domain configuration failed, enforcing in /etc/hosts...."
        known_fqdns=( $(dnsdomainname -A) )
        for item in "${!known_fqdns[@]}" ; do
            case "${known_fqdns[${item}]}" in
                *.*)
                    jane notify info "Adding FQDN: '${known_fqdns[${item}]}'..."
                    ip_index="$(( ${item} + 1 ))"
                    printf "%s\n" "127.0.1.${ip_index} ${known_fqdns[${item}]} $(hostname)" >> /etc/hosts
                    ;;
            esac
        done
    fi
    if [ "${REAL_HOSTNAME}" == "$(hostname)" ] ; then
        jane notify ok "Hostname changed successfully"
        jane notify info "Hostname: '$(hostname)'"
        jane notify info "Domain: '$(dnsdomainname)'"
        jane notify info "FQDN: '$(hostname --fqdn)'"
    else
        jane notify warning "Hostname change to '${REAL_HOSTNAME}' failed"
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

# Configure Ansible
if ! type ansible > /dev/null 2>&1 ; then
    jane notify warning "Ansible not found"

    tee "/etc/apt/sources.list" > "/dev/null" <<EOF
deb http://deb.debian.org/debian stretch main
deb http://deb.debian.org/debian stretch-updates main
deb http://deb.debian.org/debian stretch-backports main
deb http://security.debian.org/ stretch/updates main
EOF

    tee "/etc/apt/preferences.d/provision_ansible.pref" > "/dev/null" <<EOF
Package: ansible
Pin: release a=stretch-backports
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
        encfs \
        git \
        haveged \
        jo \
        jq \
        make \
        python-apt \
        python-dnspython \
        python-future \
        python-jinja2 \
        python-ldap \
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
        shellcheck \
        yamllint ${ansible_from_debian}

    jane notify cache "Cleaning up cache directories..."
    find /var/lib/apt/lists -maxdepth 1 -type f ! -name 'lock' -delete
    find /var/cache/apt/archives -maxdepth 1 -name '*.deb' -delete
    rm -rf /root/.cache/* /tmp/*
else
    jane notify ok "Ansible found at '$(which ansible)'"
    ansible --version
fi

# Update APT cache on the first boot after provisioning so that APT packages
# can be installed correctly right away.
if [ -z "${JANE_BOX_INIT:-}" ] ; then
    jane notify cache "Refreshing APT cache"
    apt-get update

    # vagrant-libvirt executes virt-sysprep during box packaging.
    # virt-sysprep zeroes out files in /usr/local/*, apparently.
    # So we need to install PyPI packages on the real box, not the template.
    jane notify install "Installing test requirements via PyPI..."
    pip install debops netaddr python-ldap dnspython passlib future testinfra ${ansible_from_pypi}
    jane notify cache "Cleaning up cache directories..."
    rm -rf /root/.cache/* /tmp/*
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

# Configure hostname and domain
REAL_HOSTNAME="ci-$(cat /proc/sys/kernel/random/uuid)"

if [ -n "${REAL_HOSTNAME}" ] ; then
    jane notify info "Changing box hostname to '${REAL_HOSTNAME}'..."
    if [ -d /run/systemd/system ] ; then
        hostnamectl set-hostname "${REAL_HOSTNAME}"
        systemctl restart networking.service
    else
        hostname "${REAL_HOSTNAME}"
        printf "%s\n" "${REAL_HOSTNAME}" > /etc/hostname
        /etc/init.d/networking restart
    fi
    jane notify ok "Hostname changed to '$(hostname)'"
    jane notify info "FQDN: '$(hostname --fqdn)'"
    jane notify info "DOMAIN: '$(dnsdomainname)'"
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

$provision_controller = <<SCRIPT
set -o nounset -o pipefail -o errexit

readonly PROVISION_ANSIBLE_FROM="#{ENV['ANSIBLE_FROM'] || 'debian'}"

jane notify info "Configuring Ansible Controller host..."

ansible_from_pypi=""
if [ "${PROVISION_ANSIBLE_FROM}" == "pypi" ] ; then
    ansible_from_pypi="ansible"
fi

jane notify install "Installing test requirements via PyPI..."
sudo pip install debops netaddr python-ldap dnspython passlib future testinfra ${ansible_from_pypi}
jane notify cache "Cleaning up cache directories..."
sudo rm -rf /root/.cache/* /tmp/*

if ! [ -e .local/share/debops/debops ] ; then
    mkdir -p src .local/share/debops
    if [ -d "/vagrant" ] ; then
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
    mkdir -p "src/controller/ansible/inventory/host_vars/$(hostname)"
    if [ -z "#{ENV['CONTROLLER']}" ] || [ "#{ENV['CONTROLLER']}" != "true" ] ; then
        printf "%s\n" "---\n\n# Use smaller DH parameters to speed up test runs\ndhparam__bits: [ '1024' ]" > "src/controller/ansible/inventory/host_vars/$(hostname)/dhparam.yml"
    fi
fi

jane notify info "Ansible Controller provisioning complete"
SCRIPT

VAGRANT_NODES = ENV['VAGRANT_NODES'] || 0
VAGRANT_NODE_BOX = ENV['VAGRANT_NODE_BOX'] || 'debian/stretch64'

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

    config.vm.define "master", primary: true do |subconfig|
        subconfig.vm.box = ENV['VAGRANT_BOX'] || 'debian/stretch64'
        subconfig.vm.provision "shell", inline: $provision_box, keep_color: true, run: "always"

        subconfig.vm.provider "libvirt" do |libvirt, override|
            # On a libvirt provider, default sync method is NFS. If we switch
            # it to 'rsync', this will drop the dependency on NFS on the host.
            override.vm.synced_folder ENV['CI_PROJECT_DIR'] || ".", "/vagrant", type: "rsync"

            override.vm.network :public_network, :dev => ENV['VAGRANT_MASTER_PUBLIC_BRIDGE'] || 'br0', :type => 'bridge'

            libvirt.random_hostname = true
            libvirt.memory = ENV['VAGRANT_MASTER_MEMORY'] || '512'

            if ENV['GITLAB_CI'] != "true"
                libvirt.memory = ENV['VAGRANT_MASTER_MEMORY'] || '1024'
            end

            if ENV['VAGRANT_BOX'] || 'debian/stretch64' == 'debian/stretch64'
                override.ssh.insert_key = false
            end
        end

        if ENV['GITLAB_CI'] != "true"
            subconfig.vm.provision "shell", inline: $provision_controller, keep_color: true, privileged: false
        end

        if Vagrant::Util::Platform.windows? then
            # MS Windows doesn't support symlinks, so disable directory sync under it.
            # DebOps will be installed normally, via 'debops-update'
            subconfig.vm.synced_folder ".", "/vagrant", disabled: true
        elsif ENV['GITLAB_CI'] == "true"
            # We are running in a GitLab CI environment
            subconfig.vm.synced_folder ENV['CI_PROJECT_DIR'] || ".", "/vagrant"
        end

        if ENV['CI'] != "true"
            subconfig.vm.post_up_message = "Thanks for trying DebOps! After logging in, run:
            cd src/controller ; debops"
        end
    end

    if VAGRANT_NODES != 0
        (1..VAGRANT_NODES.to_i).each do |i|
            config.vm.define "node#{i}", autostart: false do |node|

                node.vm.box = VAGRANT_NODE_BOX
                node.vm.provision "shell", inline: $provision_node_box, keep_color: true, run: "always"

                # Don't populate '/vagrant' directory on other nodes
                node.vm.synced_folder ".", "/vagrant", disabled: true
            end
        end
    end

end
