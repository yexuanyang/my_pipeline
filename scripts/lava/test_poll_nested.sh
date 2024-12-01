#!/bin/sh

set -e -u

cd /root
./mk.sh
cd /root/libevl-rros/build-dest/tests/
ls
./poll-nested
