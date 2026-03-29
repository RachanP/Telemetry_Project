#!/usr/bin/env python3
"""
SONiC Temperature Prometheus Exporter
ดึงค่า config จาก Environment Variables (.env / docker-compose)
"""

import os
import re
import time
import paramiko
from prometheus_client import start_http_server, REGISTRY
from prometheus_client.core import GaugeMetricFamily

# ===== CONFIG จาก Environment Variables =====
SWITCH_HOST     = os.environ.get("SWITCH_IP",              "192.168.1.11")
SWITCH_USER     = os.environ.get("SWITCH_USER",            "admin")
SWITCH_PASS     = os.environ.get("SWITCH_PASS",            "YourPaSsWoRd")
SWITCH_NAME     = os.environ.get("SWITCH_NAME",            "switch1")
EXPORTER_PORT   = int(os.environ.get("TEMP_EXPORTER_PORT", "9805"))
SCRAPE_INTERVAL = int(os.environ.get("TEMP_SCRAPE_INTERVAL","30"))
# =============================================


def ssh_get_temperature(host, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password, timeout=10)
        _, stdout, _ = client.exec_command("show platform temperature")
        return stdout.read().decode("utf-8")
    except Exception as e:
        print(f"[ERROR] SSH failed: {e}")
        return None
    finally:
        client.close()


def parse_temperature_output(output):
    sensors = []
    lines = output.strip().split("\n")
    data_started = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "Sensor" in line and "Temperature" in line:
            data_started = True
            continue
        if not data_started or line.startswith("-"):
            continue

        parts = re.split(r'\s{2,}', line)
        if len(parts) < 3:
            continue

        try:
            sensor_name = parts[0].strip()
            temp_str    = parts[1].strip()
            high_th     = parts[2].strip()
            crit_high   = parts[4].strip() if len(parts) > 4 else "N/A"
            warning     = parts[6].strip() if len(parts) > 6 else "False"

            temp          = float(temp_str)  if temp_str  not in ("N/A", "") else None
            high_th_val   = float(high_th)   if high_th   not in ("N/A", "") else None
            crit_high_val = float(crit_high) if crit_high not in ("N/A", "") else None

            if temp is not None:
                sensors.append({
                    "sensor":               sensor_name,
                    "temperature":          temp,
                    "high_threshold":       high_th_val,
                    "crit_high_threshold":  crit_high_val,
                    "warning":              1 if warning.lower() == "true" else 0,
                })
        except (ValueError, IndexError) as e:
            print(f"[WARN] Cannot parse line: {line} -> {e}")

    return sensors


class SonicTemperatureCollector:
    def collect(self):
        output = ssh_get_temperature(SWITCH_HOST, SWITCH_USER, SWITCH_PASS)
        if output is None:
            return

        sensors = parse_temperature_output(output)
        if not sensors:
            print("[WARN] No sensor data parsed")
            return

        temp_g      = GaugeMetricFamily("sonic_temperature_celsius",
                        "Current temperature", labels=["target", "sensor"])
        high_g      = GaugeMetricFamily("sonic_temperature_high_threshold_celsius",
                        "High threshold",      labels=["target", "sensor"])
        crit_g      = GaugeMetricFamily("sonic_temperature_crit_high_threshold_celsius",
                        "Critical threshold",  labels=["target", "sensor"])
        warning_g   = GaugeMetricFamily("sonic_temperature_warning",
                        "Warning status 1=warn 0=ok", labels=["target", "sensor"])

        for s in sensors:
            lv = [SWITCH_NAME, s["sensor"]]
            temp_g.add_metric(lv, s["temperature"])
            if s["high_threshold"]      is not None: high_g.add_metric(lv, s["high_threshold"])
            if s["crit_high_threshold"] is not None: crit_g.add_metric(lv, s["crit_high_threshold"])
            warning_g.add_metric(lv, s["warning"])

        yield temp_g
        yield high_g
        yield crit_g
        yield warning_g

        print(f"[INFO] Collected {len(sensors)} sensors from {SWITCH_HOST} (target={SWITCH_NAME})")


if __name__ == "__main__":
    REGISTRY.register(SonicTemperatureCollector())
    start_http_server(EXPORTER_PORT)
    print(f"[INFO] Exporter started — port={EXPORTER_PORT} switch={SWITCH_HOST} target={SWITCH_NAME}")
    while True:
        time.sleep(SCRAPE_INTERVAL)