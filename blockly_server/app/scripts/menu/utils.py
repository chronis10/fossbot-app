import os
import signal
import threading
import time
import subprocess
from collections import deque

# ----------------- Orphan-safe exit -----------------
def exit_when_parent_dies(parent_pid=None, interval=0.5):
    if parent_pid is None:
        parent_pid = os.getppid()

    def _watch():
        while True:
            try:
                ppid_now = os.getppid()
                if ppid_now != parent_pid and ppid_now == 1:
                    os.kill(os.getpid(), signal.SIGTERM)
                    return
            except Exception:
                try:
                    os.kill(os.getpid(), signal.SIGTERM)
                except Exception:
                    pass
                return
            time.sleep(interval)

    threading.Thread(target=_watch, daemon=True).start()


def get_wifi_ssid():
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"], stderr=subprocess.DEVNULL) \
                         .decode("utf-8").strip()
        return ssid if ssid else "Not Connected"
    except Exception:
        return "Not Connected"


def get_ip_address():
    try:
        out = subprocess.check_output(["hostname", "-I"], stderr=subprocess.DEVNULL) \
                        .decode("utf-8").strip()
        candidates = [x for x in out.split() if x and not x.startswith("127.")]
        ipv4 = [x for x in candidates if x.count(".") == 3]
        if ipv4:
            return ipv4[0]
        return candidates[0] if candidates else "No IP"
    except Exception:
        return "No IP"


def _to_float_or_none(x):
    try:
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        if isinstance(x, str):
            return float(x.strip().replace("%", ""))
        return None
    except Exception:
        return None


def read_battery_raw(robot):
    return robot.get_power_sensor()


# ----------------- Battery conversion + smoothing -----------------
ADC_AT_12V = 825.0
V_AT_ADC_AT_12V = 12.0

V_FULL = 12.6
V_STOP = 9.9

LOW_BATT_PCT = 10.0
LOW_BEEP_EVERY_S = 2.0

SMOOTH_WINDOW_S = 2.0
SAMPLE_EVERY_S = 0.2


def raw_to_voltage(raw, adc_at_12v=ADC_AT_12V, v_at_adc=V_AT_ADC_AT_12V):
    val = _to_float_or_none(raw)
    if val is None:
        return None
    return (val / float(adc_at_12v)) * float(v_at_adc)

def percent_from_voltage(v, v_full=V_FULL, v_stop=V_STOP):
    if v is None or v_full <= v_stop:
        return None
    pct = (v - v_stop) / (v_full - v_stop) * 100.0
    return max(0.0, min(100.0, pct))


class BatteryMonitor:
    def __init__(self, robot):
        self.robot = robot
        self._lock = threading.Lock()
        self._stop = threading.Event()

        self._raw = None
        self._v_inst = None
        self._v_smooth = None
        self._pct = None

        self._buf = deque(maxlen=max(1, int(SMOOTH_WINDOW_S /SAMPLE_EVERY_S)))
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while not self._stop.is_set():
            try:
                raw = read_battery_raw(self.robot)
                v = raw_to_voltage(raw)
                if v is not None:
                    self._buf.append(v)
                    v_smooth = sum(self._buf) / len(self._buf)
                    pct = percent_from_voltage(v_smooth)
                else:
                    v_smooth = None
                    pct = None

                with self._lock:
                    self._raw = raw
                    self._v_inst = v
                    self._v_smooth = v_smooth
                    self._pct = pct
            except Exception:
                pass

            self._stop.wait(SAMPLE_EVERY_S)

    def get(self):
        with self._lock:
            return {"raw": self._raw, "v_inst": self._v_inst, "v": self._v_smooth, "pct": self._pct}

    def stop(self):
        self._stop.set()


# ----------------- Wi-Fi helpers (Pi OS, no sudo): wpa_cli scan + connect -----------------
WIFI_IFACE = "wlan0"


def get_saved_networks():
    nets = []
    try:
        out = subprocess.check_output(
            ["wpa_cli", "-i", WIFI_IFACE, "list_networks"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore")

        lines = out.splitlines()
        if len(lines) < 2:
            return []

        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            
            net_id = parts[0]
            ssid = parts[1]
            flags = parts[3]

            if not ssid or "[P2P-GO-NEG]" in flags:
                continue

            nets.append({"id": net_id, "ssid": ssid})
        return nets
    except Exception:
        return []

def connect_saved_network(net_id):
    try:
        subprocess.check_output(["wpa_cli", "-i", WIFI_IFACE, "enable_network", net_id], stderr=subprocess.STDOUT)
        subprocess.check_output(["wpa_cli", "-i", WIFI_IFACE, "select_network", net_id], stderr=subprocess.STDOUT)
        subprocess.check_output(["wpa_cli", "-i", WIFI_IFACE, "save_config"], stderr=subprocess.STDOUT)
        subprocess.check_output(["wpa_cli", "-i", WIFI_IFACE, "reconfigure"], stderr=subprocess.STDOUT)
        return True, "Connecting..."
    except subprocess.CalledProcessError as e:
        msg = e.output.decode("utf-8", errors="ignore").strip()
        return False, (msg[:24] if msg else "Connect failed")
    except Exception:
        return False, "Connect failed"


def scan_wifi_networks(limit=30):
    nets = []
    try:
        subprocess.call(["wpa_cli", "-i", WIFI_IFACE, "scan"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        time.sleep(2.0)

        out = subprocess.check_output(
            ["wpa_cli", "-i", WIFI_IFACE, "scan_results"],
            stderr=subprocess.DEVNULL
        ).decode("-utf-8", errors="ignore")

        lines = out.splitlines()
        if len(lines) < 2:
            return []

        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) < 5:
                continue

            try:
                signal_dbm = int(parts[2])
            except Exception:
                continue

            flags = parts[3]
            ssid = parts[4].strip()
            if not ssid:
                continue

            sig = int(max(0, min(100, 2 * (signal_dbm + 100))))
            security = "WPA" if (("WPA" in flags) or ("RSN" in flags)) else "--"
            nets.append({"ssid": ssid, "signal": sig, "security": security})

        dedup = {}
        for n in nets:
            s = n["ssid"]
            if s not in dedup or n["signal"] > dedup[s]["signal"]:
                dedup[s] = n

        out = list(dedup.values())
        out.sort(key=lambda x: x.get("signal", 0), reverse=True)
        return out[:limit]
    except Exception:
        return []


def connect_wifi(ssid, password):
    if not ssid:
        return False, "No SSID"

    try:
        net_id = subprocess.check_output(
            ["wpa_cli", "-i", WIFI_IFACE, "add_network"],
            stderr=subprocess.STDOUT
        ).decode("utf-8", errors="ignore").strip()

        if not net_id.isdigit():
            return False, "add_network fail"

        subprocess.check_output(
            ["wpa_cli", "-i", WIFI_IFACE, "set_network", net_id, "ssid", f"\"{ssid}\""],
            stderr=subprocess.STDOUT
        )

        if password:
            subprocess.check_output(
                ["wpa_cli", "-i", WIFI_IFACE, "set_network", net_id, "psk", f"\"{password}\""],
                stderr=subprocess.STDOUT
            )
        else:
            subprocess.check_output(
                ["wpa_cli", "-i", WIFI_IFACE, "set_network", net_id, "key_mgmt", "NONE"],
                stderr=subprocess.STDOUT
            )

        subprocess.check_output(["wpa_cli", "-i", WIFI_IFACE, "enable_network", net_id], stderr=subprocess.STDOUT)
        subprocess.check_output(["wpa_cli", "-i", WIFI_IFACE, "select_network", net_id], stderr=subprocess.STDOUT)
        subprocess.check_output(["wpa_cli", "-i", WIFI_IFACE, "save_config"], stderr=subprocess.STDOUT)
        subprocess.check_output(["wpa_cli", "-i", WIFI_IFACE, "reconfigure"], stderr=subprocess.STDOUT)

        return True, "Connecting..."
    except subprocess.CalledProcessError as e:
        msg = e.output.decode("utf-8", errors="ignore").strip()
        return False, (msg[:24] if msg else "Connect failed")
    except Exception:
        return False, "Connect failed"

# ----------------- Bluetooth helpers -----------------

def _run_bt_command(command, timeout=10):
    """Executes a command in bluetoothctl and returns the output."""
    try:
        p = subprocess.Popen('bluetoothctl', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p.stdin.write(command + "\n")
        p.stdin.flush()
        time.sleep(2)  # Give bluetoothctl some time to process
        stdout, stderr = p.communicate(input="exit\n", timeout=timeout)
        return stdout, stderr
    except Exception as e:
        return None, str(e)

def scan_bluetooth_devices(scan_time=10):
    """Scan for bluetooth devices for a given amount of time."""
    devices = []
    try:
        p = subprocess.Popen('bluetoothctl', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        p.stdin.write("scan on\n")
        p.stdin.flush()
        time.sleep(scan_time)
        p.stdin.write("scan off\n")
        p.stdin.flush()
        
        stdout, stderr = p.communicate(input="devices\nexit", timeout=5)

        if not stdout:
            return []
        
        for line in stdout.splitlines():
            if line.strip().startswith("Device"):
                parts = line.strip().split(" ", 2)
                if len(parts) >= 3:
                    mac, name = parts[1], parts[2]
                    devices.append({"mac": mac, "name": name})
        return devices
    except Exception:
        return []

def pair_device(mac):
    """Pair with a bluetooth device."""
    out, err = _run_bt_command(f"pair {mac}")
    if err:
        return False, err
    if "Pairing successful" in out:
        return True, "Paired!"
    if out:
        return False, "\n".join(out.strip().split('\n')[-2:])
    return False, "Pairing failed"

def connect_device(mac):
    """Connect to a bluetooth device."""
    out, err = _run_bt_command(f"connect {mac}")
    if err:
        return False, err
    if "Connection successful" in out:
        return True, "Connected!"
    if out:
        return False, "\n".join(out.strip().split('\n')[-2:])
    return False, "Connection failed"

def trust_device(mac):
    """Trust a bluetooth device."""
    out, err = _run_bt_command(f"trust {mac}")
    if err:
        return False, err
    if "trust succeeded" in out:
        return True, "Trusted!"
    if out:
        return False, "\n".join(out.strip().split('\n')[-2:])
    return False, "Trust failed"