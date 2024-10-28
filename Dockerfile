# Set up an Ansible Controller with DebOps support as a Docker container
#
# Copyright (C) 2017-2019 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017-2019 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later


# Basic usage:
#
#     docker build -t debops .
#     docker run --name <container> -h controller.example.org -i -t debops
#
#     # Refresh APT cache
#     sudo apt update
#
#     cd src/controller
#     debops run common --diff


FROM debian:bullseye-slim AS builder

LABEL maintainer="Maciej Delmanowski <drybjed@gmail.com>" \
      project="DebOps" homepage="https://debops.org/"

RUN apt-get -q update \
    && DEBIAN_FRONTEND=noninteractive apt-get \
       --no-install-recommends -yq install \
       python3-pip \
       python3-setuptools \
       python3-toml \
       python3-wheel \
       python3-pypandoc \
       python3-sphinx \
       python3-sphinx-rtd-theme \
       pandoc \
       make \
       git

COPY . /root/src/debops
WORKDIR /root/src/debops
RUN make man wheel-quiet \
    && cp lib/docker/docker-entrypoint /usr/local/bin/

FROM debian:bullseye-slim

LABEL maintainer="Maciej Delmanowski <drybjed@gmail.com>" \
      project="DebOps" homepage="https://debops.org/"

RUN apt-get -q update \
    && DEBIAN_FRONTEND=noninteractive apt-get \
       --no-install-recommends -yq install \
       iproute2 \
       iputils-ping \
       vim \
       openssh-client \
       python3-apt \
       python3-cryptography \
       python3-distro \
       python3-dnspython \
       python3-future \
       python3-ldap \
       python3-netaddr \
       python3-pip \
       python3-setuptools \
       python3-toml \
       python3-wheel \
       procps \
       sudo \
       tree \
       sshpass \
       make \
       git \
       man-db \
    && pip3 install ansible \
    && echo "Cleaning up cache directories..." \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*.deb /root/.cache/*

COPY --from=builder /root/src/debops/dist /root/src/debops/dist
COPY --from=builder /usr/local/bin/docker-entrypoint /usr/local/bin/docker-entrypoint

RUN pip3 install /root/src/debops/dist/debops-*.whl \
    && chmod +x /usr/local/bin/docker-entrypoint \
    && rm -rf /root/src /root/.cache/*

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

ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
CMD ["/bin/bash"]
