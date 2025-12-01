AutoBG – Konfigurierbarer Auto-Klicker & Auto-Key-Presser (Windows)

Ein leistungsstarker, vollständig konfigurierbarer Auto-Klicker &
Auto-Key-Presser für Windows. Unterstützt Tastendrücke, ScanCodes,
Stealth-Modus, Mausklicks, Fenster-Fokus-Wechsel, Hotkeys,
non-interaktiven CLI-Modus und Ziel-Fenster-Erkennung.

Features: - Hintergrund-Tastendruck (PostMessage) - Stealth-Modus -
Voller Maus-Support - Intervall konfigurierbar - Key-Selector oder
Lernmodus - Fenster-Auswahl - Hotkeys - Debug-Modus - ScanCode + VK
Input - CLI-Modus

Installation: git clone https://github.com/DEINUSERNAME/AutoBG cd AutoBG
python -m pip install –upgrade pip pip install -r requirements.txt

Starten: python autog_bg_attach_configurable.py

Hotkeys: F9 - Start/Stop F10 - Stop F12 - Beenden F8 - Fenster wählen
F6 - Stealth an/aus F7 - Debug an/aus F4 - Intervall ändern F3 - Taste
ändern

Maus-Modus: python autog_bg_attach_configurable.py –mouse

CLI Beispiel: python autog_bg_attach_configurable.py –noninteractive
–title “Notepad” –key g –interval 1.5

Stealth Mode: –stealth on


Lizenz: MIT License
