# Russound-Web
Simple Python local Web serial interface and app for the Russound CAV system to replace the defunct TCH1.
Runs on Raspberry Pi in my case.
Need a USB to serial adapter cable to connect to the Russound CAV.
Only exposing power, volume and source selection (for now).
Zone/controller/source information is hard-coded in (for now).
See three attached screenshots for how the interface looks.

Edit dhcpcd.conf to fix the wifi dhcp address on 
boothp. 

To make launcher.sh run on reboot:

chmod 755 launcher.sh

mkdir logs (for output log - not needed for real instance as it uses memory)

sudo crontab -e

Add "@reboot sh /home/pi/launcher.sh >/home/pi/logs/cronlog 2>&1" (take out the output log for real instance: "@reboot sh /home/pi/launcher.sh &")

sudo reboot (to test)

Make sure russound_app.py has execution right:
"chmod a+x russound_app.py"


# Major Update May 2026

Architecture

Migrated from http.server to Flask
Externalized all settings to config.json (auto-created with defaults on first run)
Added threading.Lock() across all serial port access to prevent collisions
All serial commands run in background threads for instant HTTP response
Added gunicorn support (single worker, shared serial port)

New Pages & Routes

GET /admin — admin settings page
POST /admin/save — saves config to disk, hot-reloads names/presets immediately
POST /admin/restart — re-execs the Python process cleanly
GET /api/status — returns status for all zones at once
GET /api/status/<zone_index> — returns status for a single zone (used for sequential load)
POST /api/party — sets source and volume on all zones simultaneously
POST /api/reconnect — closes and re-opens the serial connection after a failure

Main Screen (index.html)

Full redesign — iOS-style cards, auto dark/light theme (prefers-color-scheme)
Zone status loads sequentially per zone to avoid serial port collisions
On/Off buttons use fetch() — no page reload
Optimistic UI updates with rollback on failure
Toast notifications for failed commands
Auto-refresh every 30 seconds (picks up wall keypad changes)
All On button opens a modal to choose source and volume for all zones
Source badge (colored pill) on each zone card showing active source when on
Marquee scroll for zone names longer than 12 characters
Tap zone name/status area to navigate to zone detail (in addition to › button)
Health indicator dot in header (green/orange/red) reflecting serial connection state
Automatic serial reconnect attempt if all zones fail two refreshes in a row
Gear icon (⚙) links to admin page

Zone Detail Screen (zone.html)

Full redesign — power, source, volume in card sections
Source buttons highlight the currently active source on page load
Volume slider with quick-preset buttons (25/50/75/100%)
Power buttons dim the inactive state to show current on/off state
Controller and zone number shown in header subtitle (e.g. "Controller 1 · Zone 4")
Toast + rollback on failed commands

Admin Screen (admin.html) — new

Edit zone names (capped at controller_count × 6)
Edit source names
Edit volume presets
Edit host IP and port (restart reminder shown if changed)
Serial port settings intentionally not editable (too dangerous)
Restart button with confirmation modal; polls until server comes back online
Zone limit enforced in UI (Add Zone button blocked at max, validated on save)

Config (config.json)

All settings externalized: host, port, serial_port, baud, controller_count, zone_names, source_names, volume_presets
Zone list automatically trimmed to controller_count × 6 on load

