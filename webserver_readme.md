# Webserver für stadtrevue

Web Serial braucht `http://localhost` — `file://` funktioniert nicht.

## Python installieren (Windows)

1. https://www.python.org/downloads/
2. Installer starten → **“Add Python to PATH”** ankreuzen
3. Terminal testen: `python --version`

## Server starten

Im Projektordner:

```powershell
cd C:\Pfad\zu\stadtrevue
python server.py
```

Browser: **http://localhost:8080**

Mac/Linux:

```bash
cd /Pfad/zu/stadtrevue
python3 server.py
```

## Medien & Config

1. Dateien in den Ordner `media/` legen (mp4, mp3, jpg, …)
2. **http://localhost:8080/admin.html** öffnen
3. Pro Button (a–j) Datei und optional Titel zuordnen → Speichern
4. Kiosk: **http://localhost:8080**

## Kiosk-Start (Windows)

`start-kiosk.bat` im Projektordner anlegen:

```bat
@echo off
cd /d C:\Pfad\zu\stadtrevue
start /min python server.py
timeout /t 2 /nobreak >nul
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk http://localhost:8080
```

Pfad anpassen. Doppelklick startet Server + Chrome im Fullscreen.

Autostart: `Win + R` → `shell:startup` → Verknüpfung zur `.bat` ablegen.

## Pico verbinden

1. Pico per USB
2. Chrome/Edge → http://localhost:8080
3. Einmal **Connect** klicken, Port wählen
4. Danach reconnectet Chrome beim Reload automatisch

Browser: Chrome oder Edge (Web Serial). Firefox/Safari gehen nicht.

Debug-Zeile in index.html: **Leertaste** ein/aus.
