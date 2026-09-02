# PlatformIO

## Projekt öffnen

PlatformIO braucht eine `platformio.ini`. Die liegt **nicht** im Root, sondern in:

- `pico-button-test/` — Pico-Firmware (10 Buttons)

### Option A (empfohlen)

Cursor/VS Code: **File → Open Workspace from File…** → `stadtrevue.code-workspace`

Dann in der PlatformIO-Sidebar unten das Projekt `pico-button-test` wählen.

### Option B

Nur den Unterordner öffnen: **File → Open Folder…** → `pico-button-test`

### Option C

Root `stadtrevue` offen lassen — `.vscode/settings.json` hat `multiProjects: true`. PlatformIO-Sidebar → **Pick Project Folder** → `pico-button-test` wählen.

## Upload

1. Pico per USB
2. Beim ersten Mal: BOOTSEL gedrückt halten, USB rein → `RPI-RP2` erscheint
3. PlatformIO: **Upload** (Pfeil)
4. **Monitor** für Serial (115200)

## Build dauert beim ersten Mal

PlatformIO lädt dann Toolchain + Board-Support (~100–200 MB).
