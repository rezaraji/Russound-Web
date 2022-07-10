#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi
sleep 10s
sudo python3 russound_app.py
cd /
