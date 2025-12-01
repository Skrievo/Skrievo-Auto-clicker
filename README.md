# 🖱️ Skrievo – Auto Clicker & Auto Key Presser (Windows)

Skrievo – Auto Clicker & Auto Key Presser ist ein leistungsstarker und flexibel konfigurierbarer Auto-Klicker & Auto-Key-Presser für Windows.  
Er unterstützt Tastatur- und Mausaktionen, Stealth-Modus, Fenster-Zuweisung, Hotkeys und Full-CLI-Automation.

---

## 🚀 Features

- ✔ Hintergrund-Tastatureingaben (PostMessage)
- ✔ Stealth-Modus (fokussiert das Ziel-Fenster kurz, führt Aktion aus und gibt Fokus zurück)
- ✔ Voller Maus-Support (Linksklick, Rechtsklick, Doppelklick, Positionieren)
- ✔ Lernmodus zur automatischen Tastenerkennung
- ✔ Fenster-Auswahl (Liste oder CLI)
- ✔ Hotkey-Steuerung
- ✔ Debug-Modus
- ✔ ScanCode + VirtualKey-Support
- ✔ Vollständig automatisierbarer CLI-Modus

---

## 📦 Installation

### 1. Repository klonen
```bash
git clone https://github.com/Skrievo/Skrievo-Auto-clicker

```

### 2. Abhängigkeiten installieren
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Starten

```bash
python ./auto.py
```

---

## ⌨️ Hotkeys

| Hotkey | Funktion |
|--------|----------|
| F9  | Start / Stop |
| F10 | Stoppen |
| F12 | Programm beenden |
| F8  | Fenster auswählen |
| F6  | Stealth an/aus |
| F7  | Debug-Modus |
| F4  | Intervall ändern |
| F3  | Taste ändern |

---



---

## 🧠 CLI-Modus

```bash
python autog_bg_attach_configurable.py --noninteractive --title "Notepad" --key g --interval 1.5
```

---

## 🔒 Stealth Mode

```bash
--stealth on
```

---



## 📄 Lizenz

MIT License


