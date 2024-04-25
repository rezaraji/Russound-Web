# Russound-Web
Simple Python local Web serial interface and app for the Russound CAV system to replace the defunct TCH1.
Runs on Raspberry Pi in my case.
Need a USB to serial adapter cable to connect to the Russound CAV.
Only exposing power, volume and source selection (for now).
Zone/controller/source information is hard-coded in (for now).
See three attached screenshots for how the interface looks.

Put this in Crontab (sudo crontab -e) to always run on startup:
"@reboot python3 /home/pi/russound_app.py &"

Make sure russound_app.py has execution right:
"chmod a+x russound_app.py"
