#!/bin/bash
rustup override set beta-2021-06-23-x86_64-unknown-linux-gnu
rustup component add rust-src
cp /root/my_pipeline/scripts/config/rros_defconfig_la .config
touch /tmp/compile.txt
