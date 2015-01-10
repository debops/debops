#!/bin/sh

LOCK="this-authority-is-locked"

if [ ! -e ${LOCK} ] ; then
  if [ -n "$1" ]; then
    openssl ca -config .db/openssl.cnf -revoke $1
    make regenerate-certificate-revocation-lists
    rm -frv .db/certs/$(basename $1) $1 requests/$(basename -s .crt $1).csr
  else
    echo "Specify a certificate file to revoke:"
    find certs -maxdepth 1 -type f -name '*.crt'
  fi
else
  echo "Cannot revoke, this authority is locked"
  exit 1
fi


