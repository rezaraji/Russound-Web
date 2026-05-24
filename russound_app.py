"""
Reza Raji
July 2022 — Flask rewrite 2026

Simple app to replace the now discontinued and defunct Russound TCH1 unit.
Uses a converted russound RNET library to work on serial port (russound_serial.py).

Run with:
    python russound_app.py
Or via gunicorn for production:
    gunicorn -w 1 -b 0.0.0.0:8000 russound_app:app
(Note: use only 1 worker since the serial port is a shared resource.)
"""

import json
import os
import sys
import threading
import russound_serial
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# ── Configuration ─────────────────────────────────────────────────────────────

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

_DEFAULTS = {
    "host": "192.168.1.200",
    "port": 8000,
    "serial_port": "/dev/ttyUSB0",
    "baud": 19200,
    "controller_count": 2,
    "zone_names": [
        "Guest Bath", "Dining Room", "Kitchen", "Master Bed", "Master Bath", "Nick",
        "Office", "Play Room", "Alex", "Living Room", "Patio", "Pool"
    ],
    "source_names": ["Sonos", "Apple"],
    "volume_presets": [25, 50, 75, 100]
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        # Fill in any missing keys with defaults
        return {**_DEFAULTS, **data}
    else:
        # Write defaults to disk on first run so the user has a file to edit
        with open(CONFIG_FILE, 'w') as f:
            json.dump(_DEFAULTS, f, indent=2)
        print(f"Created default config file at {CONFIG_FILE}")
        return dict(_DEFAULTS)

_config = load_config()

HOST             = _config['host']
PORT             = _config['port']
SERIAL_PORT      = _config['serial_port']
BAUD             = _config['baud']
CONTROLLER_COUNT = _config['controller_count']
ZONE_NAMES       = _config['zone_names'][:CONTROLLER_COUNT * 6]   # max 6 zones per controller
SOURCE_NAMES     = _config['source_names']
VOLUME_PRESETS   = _config['volume_presets']

# ── Russound connection ────────────────────────────────────────────────────────

russound = russound_serial.Russound(SERIAL_PORT, BAUD)

# Single lock protecting all serial port access across threads
serial_lock = threading.Lock()

# ── Helper functions ───────────────────────────────────────────────────────────

def controller_id(zone_name):
    return str(int(ZONE_NAMES.index(zone_name) / 6) + 1)

def zone_id(zone_name):
    return str((ZONE_NAMES.index(zone_name) % 6) + 1)

def source_id(source_name):
    return str(SOURCE_NAMES.index(source_name))

def run_bg(fn, *args):
    """Run a serial command in a background thread and return immediately."""
    threading.Thread(target=fn, args=args, daemon=True).start()

def _all_off_bg():
    with serial_lock:
        for ctrl in range(1, CONTROLLER_COUNT + 1):
            for zone in range(1, 7):
                russound.set_power(str(ctrl), str(zone), '0')

def _all_on_bg():
    with serial_lock:
        for ctrl in range(1, CONTROLLER_COUNT + 1):
            for zone in range(1, 7):
                russound.set_power(str(ctrl), str(zone), '1')

def _set_power_bg(ctrl, zone, state):
    with serial_lock:
        russound.set_power(ctrl, zone, state)

def _set_source_bg(ctrl, zone, src):
    with serial_lock:
        russound.set_source(ctrl, zone, src)

def _set_volume_bg(ctrl, zone, level):
    with serial_lock:
        russound.set_volume(ctrl, zone, level)

# ── Flask app ──────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = 'russound-secret-key'


@app.route('/')
def index():
    return render_template('index.html', zones=ZONE_NAMES, sources=SOURCE_NAMES,
                           volume_presets=VOLUME_PRESETS)


@app.route('/admin')
def admin():
    cfg = load_config()
    return render_template('admin.html', config=cfg)


@app.route('/admin/save', methods=['POST'])
def admin_save():
    try:
        data = request.get_json(force=True)
        # Validate required fields
        required = ['host', 'port', 'zone_names', 'source_names', 'volume_presets']
        for key in required:
            if key not in data:
                return jsonify(ok=False, error=f'Missing field: {key}'), 400
        # Preserve serial port settings — not editable from the UI
        existing = load_config()
        data['serial_port']      = existing['serial_port']
        data['baud']             = existing['baud']
        data['controller_count'] = existing['controller_count']
        # Write to disk
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        # Update in-memory values (takes effect immediately for names/presets;
        # host/port require restart)
        global ZONE_NAMES, SOURCE_NAMES, VOLUME_PRESETS
        ZONE_NAMES     = data['zone_names'][:CONTROLLER_COUNT * 6]
        SOURCE_NAMES   = data['source_names']
        VOLUME_PRESETS = data['volume_presets']
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route('/api/reconnect', methods=['POST'])
def api_reconnect():
    """Attempt to re-open the serial connection after a failure."""
    global russound
    try:
        with serial_lock:
            try:
                russound.ser.close()
            except Exception:
                pass
            russound = russound_serial.Russound(SERIAL_PORT, BAUD)
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route('/api/party', methods=['POST'])
def api_party():
    """Set source (and optionally volume) on all zones."""
    try:
        data = request.get_json(force=True)
        source_name = data.get('source')
        volume = data.get('volume')
        if source_name not in SOURCE_NAMES:
            return jsonify(ok=False, error='unknown source'), 400
        src = source_id(source_name)

        def _party_bg():
            with serial_lock:
                for ctrl in range(1, CONTROLLER_COUNT + 1):
                    for zone in range(1, 7):
                        russound.set_source(str(ctrl), str(zone), src)
                        if volume is not None:
                            russound.set_volume(str(ctrl), str(zone), int(volume))
        run_bg(_party_bg)
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


@app.route('/admin/restart', methods=['POST'])
def admin_restart():
    """Re-exec the current process after a short delay (gives the response time to send)."""
    def _do_restart():
        import time
        time.sleep(0.5)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    threading.Thread(target=_do_restart, daemon=True).start()
    return jsonify(ok=True)


@app.route('/go')
def zone_detail():
    current_zone = session.get('current_zone')
    if not current_zone or current_zone not in ZONE_NAMES:
        return redirect(url_for('index'))
    return render_template(
        'zone.html',
        zone=current_zone,
        zone_index=ZONE_NAMES.index(current_zone),
        sources=SOURCE_NAMES,
        volume_presets=VOLUME_PRESETS,
    )


@app.route('/api/status/<int:zone_index>')
def api_status_zone(zone_index):
    """Return status for a single zone by index (0-based)."""
    if zone_index < 0 or zone_index >= len(ZONE_NAMES):
        return jsonify(error='invalid zone'), 400
    zone_name = ZONE_NAMES[zone_index]
    ctrl = controller_id(zone_name)
    zn = zone_id(zone_name)
    try:
        with serial_lock:
            info = russound.get_zone_info(ctrl, zn, 4)
        if info is not None:
            power = info[0]
            src = info[1]
            volume = info[2] * 2
            src_name = SOURCE_NAMES[src] if src < len(SOURCE_NAMES) else f'Source {src+1}'
            return jsonify(name=zone_name, power=power, source=src, source_name=src_name, volume=volume)
        else:
            return jsonify(name=zone_name, power=None, source=None, source_name=None, volume=None)
    except Exception:
        return jsonify(name=zone_name, power=None, source=None, source_name=None, volume=None)


@app.route('/post', methods=['POST'])
def handle_post():
    button = request.form.get('button', '')

    parts = button.split(', ', 1)
    if len(parts) != 2:
        return redirect(url_for('index'))

    cmd, payload = parts[0], parts[1]
    current_zone = session.get('current_zone', '')

    if cmd == 'Go':
        session['current_zone'] = payload
        return redirect(url_for('zone_detail'))

    if cmd == 'Back':
        return redirect(url_for('index'))

    if cmd == 'Off' and payload == 'All':
        run_bg(_all_off_bg)
        return redirect(url_for('index'))

    if cmd == 'On' and payload == 'All':
        run_bg(_all_on_bg)
        return redirect(url_for('index'))

    if cmd == 'On' and payload != 'zone' and payload != 'All':
        run_bg(_set_power_bg, controller_id(payload), zone_id(payload), '1')
        return redirect(url_for('index'))

    if cmd == 'Off' and payload != 'All' and payload != 'zone':
        run_bg(_set_power_bg, controller_id(payload), zone_id(payload), '0')
        return redirect(url_for('index'))

    if cmd == 'On' and payload == 'zone':
        if current_zone:
            run_bg(_set_power_bg, controller_id(current_zone), zone_id(current_zone), '1')
        return redirect(url_for('zone_detail'))

    if cmd == 'Off' and payload == 'zone':
        if current_zone:
            run_bg(_set_power_bg, controller_id(current_zone), zone_id(current_zone), '0')
        return redirect(url_for('zone_detail'))

    if cmd == 'Source':
        if current_zone and payload in SOURCE_NAMES:
            run_bg(_set_source_bg, controller_id(current_zone), zone_id(current_zone), source_id(payload))
        return redirect(url_for('zone_detail'))

    if cmd.startswith('vol') and current_zone:
        try:
            level = int(cmd[3:])
            if 0 <= level <= 100:
                run_bg(_set_volume_bg, controller_id(current_zone), zone_id(current_zone), level)
        except ValueError:
            pass
        return redirect(url_for('zone_detail'))

    return redirect(url_for('index'))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f"Server starting on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
