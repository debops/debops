# Set up an Ansible Controller with DebOps support as a Docker container
#
# Copyright (C) 2017-2019 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017-2019 DebOps project https://debops.org/


# Basic usage:
#
#     docker build -t debops .
#     docker run --name <container> -h controller.example.org -i -t debops
#
#     cd src/controller
#     debops common --diff


FROM debian:buster-slim

LABEL maintainer="Maciej Delmanowski <drybjed@gmail.com>" \
      project="DebOps" homepage="https://debops.org/"

RUN apt-get -q update \
    && DEBIAN_FRONTEND=noninteractive apt-get \
       --no-install-recommends -yq install \
       iproute2 \
       iputils-ping \
       levee \
       openssh-client \
       python3-apt \
       python3-distro \
       python3-dnspython \
       python3-future \
       python3-ldap \
       python3-openssl \
       python3-pip \
       python3-wheel \
       python3-setuptools \
       procps \
       sudo \
       tree \
    && pip3 install \
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

# Docker does not set expected environment variables by default
# Ref: https://stackoverflow.com/questions/54411218/
ENV USER ansible

# Add contents of the DebOps monorepo to the container
# with the right permissions
COPY --chown=ansible:ansible . .local/share/debops/debops

ENTRYPOINT ["/home/ansible/.local/share/debops/debops/lib/docker/docker-entrypoint"]
CMD ["/bin/bash"]
