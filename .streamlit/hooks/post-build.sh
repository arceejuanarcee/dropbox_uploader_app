#!/bin/bash
echo "✅ post-build.sh started"
apt-get update && apt-get install -y wget gnupg curl unzip
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb
