# Auto-Key (überarbeitet)

Kurze Anleitung, um das Skript lokal unter Windows auszuführen.

Voraussetzungen
- Python 3.8+ installiert
- PowerShell (Standard unter Windows)

Installation (PowerShell)
```powershell
cd "c:\Users\geber\Desktop\Arbeit"
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Dateien
- `auto.py` : Überarbeitete Python-Version des ursprünglichen Skripts
- `requirements.txt` : Benötigte Python-Pakete (`keyboard`, `pywin32`)

Starten
```powershell
python .\auto.py
```

Hinweise
- Falls beim Import von `keyboard` oder `win32gui` Fehler auftreten: Stelle sicher, dass du die in `requirements.txt` gelisteten Pakete installiert hast.
- Das alte `auto.js` im Verzeichnis enthält die ursprüngliche Datei (falls vorhanden). Die neue Hauptdatei ist `auto.py`.

Sicherheits- und Berechtigungswunsch
- Das Skript emuliert Tastendrücke und greift auf Fenster-Funktionen zu. Führe es nur in einer vertrauenswürdigen Umgebung aus.
