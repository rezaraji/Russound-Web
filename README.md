# Russound-Web
Simple Python local Web serial interface and app for the Russound CAV system to replace the defunct TCH1.
Runs on Raspberry Pi in my case.
Need a USB to serial adapter cable to connect to the Russound CAV.
Only exposing power, volume and source selection (for now).
Zone/controller/source information is hard-coded in (for now).
See three attached screenshots for how the interface looks.

To make launcher.sh run on reboot:

chmod 755 launcher.sh
mkdir logs (for output log - not needed for real instance as it uses memory)
sudo crontab -e
Add "@reboot sh /home/pi/launcher.sh >/home/pi/logs/cronlog 2>&1" (take out the output log for real instance: "@reboot sh /home/pi/launcher.sh &")

sudo reboot (to test)

Make sure russound_app.py has execution right:
"chmod a+x russound_app.py"
