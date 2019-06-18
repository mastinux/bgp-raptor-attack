#!/bin/bash

reset

echo "Generating certificate ..."

sudo rm ~/chutney/net/nodes/000authority/keys/authority_identity_key

~/tor/src/tools/tor-gencert --create-identity-key --passphrase-fd - -i ~/chutney/net/nodes/000authority/keys/authority_identity_key -s ~/chutney/net/nodes/000authority/keys/authority_signing_key -c ~/chutney/net/nodes/000authority/keys/authority_certificate -m 12 -a 15.3.0.1:7000 -v < `echo passphrase.txt`

# TODO genera in modo automatico torrc

echo "Generating torrc ..."

~/tor/src/app/tor --ignore-missing-torrc -f ~/chutney/net/nodes/000authority/torrc --list-fingerprint --orport 1 --datadirectory ~/chutney/net/nodes/000authority

#~/tor/src/app/tor --ignore-missing-torrc -f ~/chutney/net/nodes/001guard/torrc --list-fingerprint --orport 1 --datadirectory ~/chutney/net/nodes/001guard
#~/tor/src/app/tor --ignore-missing-torrc -f ~/chutney/net/nodes/002exit/torrc --list-fingerprint --orport 1 --datadirectory ~/chutney/net/nodes/002exit

