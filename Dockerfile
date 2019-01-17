# Set up an Ansible Controller with DebOps support as a Docker container
#
# Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017 DebOps project https://debops.org/


# Basic usage:
#
#     docker build -t debops .
#     docker run --name <container> -h controller.example.org -i -t debops
#
#     cd src/controller
#     debops --skip-tags role::ferm,role::sysctl,role::sshd,role::root_account,role::etc_services
#
# These roles currently have issues when executed against a Docker container:
# - debops.etc_services   - destroys '/etc/services' file
# - debops.ferm           - cannot configure sysctl
# - debops.sshd           - daemon cannot be restarted
# - debops.sysctl         - cannot configure sysctl
# - debops.root_account   - cannot reconfigure root account


FROM debian:stretch-slim

LABEL maintainer="Maciej Delmanowski <drybjed@gmail.com>" \
      project="DebOps" homepage="https://debops.org/"

ENV DOCKER_ENVIRONMENT true

RUN apt-get -q update \
    && DEBIAN_FRONTEND=noninteractive apt-get \
       --no-install-recommends -yq install \
       iproute2 \
       levee \
       python-apt \
       python-dnspython \
       python-future \
       python-ldap \
       python-pip \
       python-wheel \
       python-setuptools \
       procps \
       sudo \
       tree \
    && pip install \
       debops[ansible] \
    && echo "Cleaning up cache directories..." \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*.deb /root/.cache/*

RUN groupadd --system admins \
    && echo "%admins ALL = (ALL:ALL) NOPASSWD: SETENV: ALL" > /etc/sudoers.d/admins \
    && chmod 0440 /etc/sudoers.d/admins \
    && useradd --user-group --create-home --shell /bin/bash \
       --home-dir /home/ansible --groups admins ansible

# Switch to the unprivileged user
USER ansible
WORKDIR /home/ansible

# Add contents of the DebOps monorepo to the container
COPY . .local/share/debops/debops

ENTRYPOINT ["/home/ansible/.local/share/debops/debops/lib/docker/docker-entrypoint"]
CMD ["/bin/bash"]
