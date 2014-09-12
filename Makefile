#!/usr/bin/make

# DebOps Makefile: install, update, uninstall DebOps scripts
# Copyright (C) 2014 Maciej Delmanowski <drybjed@gmail.com>
# Part of the DebOps project - http://debops.org/


PREFIX="/usr/local"
BIN_DIR="${PREFIX}/bin"
SHARE_DIR="${PREFIX}/share/debops"
SKEL_DIR="${SHARE_DIR}/skel"


install: install-scripts install-skel install-playbook

install-scripts:
	@echo "Installing DebOps scripts in ${BIN_DIR} ..."
	@test -d ${BIN_DIR} || mkdir -p ${BIN_DIR}
	@cp bin/debops ${BIN_DIR}/debops
	@cp bin/debops-task ${BIN_DIR}/debops-task
	@cp bin/debops-init ${BIN_DIR}/debops-init
	@cp bin/debops-update ${BIN_DIR}/debops-update

install-skel:
	@echo "Installing inventory skeleton ..."
	@test -d ${SKEL_DIR} || mkdir -p ${SKEL_DIR}
	@cp -r share/debops/skel/. ${SKEL_DIR}

install-playbook:
	@echo "Installing DebOps playbooks and roles in ${SHARE_DIR} ..."
	@debops-update ${SHARE_DIR}

clean: clean-scripts clean-skel clean-playbook

clean-scripts:
	@echo "Cleaning up DebOps scripts ..."
	@rm -f ${BIN_DIR}/debops*

clean-skel:
	@echo "Cleaning up inventory skeleton ..."
	@rm -rf ${SKEL_DIR}

clean-playbook:
	@echo "Cleaning up DebOps playbook ..."
	@rm -rf ${SHARE_DIR}

