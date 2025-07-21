#!/bin/bash
echo "✅ post-build.sh started" > build.log
apt-get update >> build.log 2>&1
apt-get install -y wget gnupg curl unzip >> build.log 2>&1
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb >> build.log 2>&1
apt install -y ./google-chrome-stable_current_amd64.deb >> build.log 2>&1
which google-chrome >> build.log
google-chrome --version >> build.log 2>&1
