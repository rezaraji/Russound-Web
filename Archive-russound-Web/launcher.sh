#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi

#enough wait for IP address to be acquired
sleep 20s

sudo python3 russound_app.py
cd /
