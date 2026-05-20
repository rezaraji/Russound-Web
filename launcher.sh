#!/bin/sh
# launcher.sh
# Navigate to the project directory, wait for network, then start the Flask app.
#
# Dependencies — install once on the Pi:
#   pip3 install flask pyserial
#
# To run on reboot (no log):
#   sudo crontab -e
#   Add: @reboot sh /home/pi/Russound-Web/launcher.sh &
#
# To run on reboot (with log):
#   Add: @reboot sh /home/pi/Russound-Web/launcher.sh >/home/pi/logs/cronlog 2>&1

cd /
cd /home/pi
sleep 20s
sudo python3 russound_app.py
cd /