Import("env")

import glob
import os
import subprocess
import time

PICO_SERIAL = "E66540F0A37B272C"

picotool = os.path.join(
    env.PioPlatform().get_package_dir("tool-picotool-rp2040-earlephilhower") or "",
    "picotool",
)

env.Replace(
    UPLOADER=picotool,
    UPLOADCMD=f'"{picotool}" load -v -x "$SOURCE"',
)
env.BoardConfig().update("upload.use_1200bps_touch", False)


def bootsel_device_count():
    result = subprocess.run(
        [picotool, "info", "-d"],
        capture_output=True,
        check=False,
    )
    return result.stdout.count(b"type:")


def eject_rp2_volume():
    volume = "/Volumes/RPI-RP2"
    if os.path.exists(volume):
        print("RPI-RP2 auswerfen (verhindert macOS-Auswurf-Warnung)...")
        subprocess.run(["diskutil", "eject", volume], check=False)
        time.sleep(0.3)


def find_pico_port():
    try:
        from serial.tools.list_ports import comports
    except ImportError:
        comports = None

    if comports:
        for port in comports():
            if port.serial_number == PICO_SERIAL:
                return port.device

    ports = glob.glob("/dev/cu.usbmodem*")
    return ports[0] if len(ports) == 1 else None


def prepare_upload(source, target, env):
    if bootsel_device_count() == 0:
        upload_port = find_pico_port()
        if not upload_port:
            print("Pico nicht gefunden — USB-Kabel prüfen.")
            env.Exit(1)

        print(f"Reset in BOOTSEL via {upload_port}...")
        env.TouchSerialPort(upload_port, 1200)
        time.sleep(0.5)

        for _ in range(20):
            if bootsel_device_count() > 0:
                break
            time.sleep(0.25)

        if bootsel_device_count() == 0:
            print("BOOTSEL-Modus nicht erreicht — BOOTSEL-Taste beim Einstecken drücken.")
            env.Exit(1)

    for _ in range(10):
        eject_rp2_volume()
        if not os.path.exists("/Volumes/RPI-RP2"):
            break
        time.sleep(0.2)


def wait_for_serial_after_upload(source, target, env):
    print("Warte auf Pico nach Upload...")
    for _ in range(40):
        if glob.glob("/dev/cu.usbmodem*"):
            print("Pico erkannt:", glob.glob("/dev/cu.usbmodem*")[0])
            return
        time.sleep(0.25)
    print("Pico noch nicht sichtbar — USB kurz abziehen und wieder einstecken.")


env.AddPreAction("upload", prepare_upload)
env.AddPostAction("upload", wait_for_serial_after_upload)
