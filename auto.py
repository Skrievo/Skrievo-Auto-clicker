# autog_bg_attach_configurable.py
import time
import threading
import ctypes
import sys
import argparse
import logging
import signal

try:
    import keyboard
    import win32gui
    import win32con
    import win32api
    import win32process
except Exception as e:
    print("Fehlende Abhängigkeit oder Import-Fehler:", e)
    print("Bitte zuerst die Anforderungen installieren: `pip install -r requirements.txt`")
    sys.exit(1)

# color output (optional)
try:
    import colorama
    from colorama import Fore, Style
    colorama.init()
    _HAS_COLORAMA = True
except Exception:
    Fore = None
    Style = None
    _HAS_COLORAMA = False

_SEP = "=" * 115
_ASCII = r"""
  ___________           .__                       _____          __                  .__  .__        __                 
 /   _____/  | _________|__| _______  ______     /  _  \  __ ___/  |_  ____     ____ |  | |__| ____ |  | __ ___________ 
 \_____  \|  |/ /\_  __ \  |/ __ \  \/ /  _ \   /  /_\  \|  |  \   __\/  _ \  _/ ___\|  | |  |/ ___\|  |/ // __ \_  __ \
 /        \    <  |  | \/  \  ___/\   (  <_> ) /    |    \  |  /|  | (  <_> ) \  \___|  |_|  \  \___|    <\  ___/|  | \/
/________  /__|_ \ |__|  |__|\___  >\_/ \____/  \____|__  /____/ |__|  \____/   \___  >____/__|\___  >__|_ \\___  >__|   
        \/     \/               \/                     \/                                     
"""

if _HAS_COLORAMA:
    print(Fore.RED + "\n" + _SEP)
    print(_ASCII)
    print(_SEP + Style.RESET_ALL + "\n")
else:
    print("\n" + _SEP)
    print(_ASCII)
    print(_SEP + "\n")


class INPUTUNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_uint),
        ("time", ctypes.c_uint),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_uint), ("union", INPUTUNION)]

SendInput = user32.SendInput
SendInput.argtypes = (ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int)
SendInput.restype = ctypes.c_uint

MapVirtualKeyW = user32.MapVirtualKeyW
MapVirtualKeyW.argtypes = (ctypes.c_uint, ctypes.c_uint)
MapVirtualKeyW.restype = ctypes.c_uint

# ====== Key-Konfiguration (VK/SC) ======
VK_KEY = 0x47   # Default: 'G'
SC_KEY = 0x22   # Default: ScanCode von 'G'

def _vk_from_char(ch: str) -> int:
    ch = ch.strip()
    if not ch:
        return 0
    if len(ch) == 1:
        return ord(ch.upper())
    # F-Tasten erlauben (F1..F24)
    if ch.upper().startswith("F"):
        try:
            n = int(ch[1:])
            if 1 <= n <= 24:
                return 0x70 + (n - 1)  # VK_F1 = 0x70
        except:
            pass
    return 0

def _sc_from_vk(vk: int) -> int:
    sc = MapVirtualKeyW(vk, MAPVK_VK_TO_VSC)
    return sc if sc is not None else 0

def configure_key_interactive():
    global VK_KEY, SC_KEY, INTERVAL
    # Intervall
    try:
        s = input(f"Intervall in Sekunden (aktuell {INTERVAL}): ").strip()
        if s:
            val = float(s.replace(",", "."))
            if val <= 0:
                print("Intervall muss > 0 sein, unverändert.")
            else:
                INTERVAL = val
    except Exception:
        print("Ungültiges Intervall, unverändert.")

    # Taste
    print("\nTaste wählen:")
    print("- Entweder **ein Zeichen** eintippen (z. B. g, e oder F5)")
    print("- Oder einfach **Enter** drücken, dann Lernmodus: Taste einmal drücken.")
    s = input("Taste eingeben (oder Enter für Lernmodus): ").strip()

    if s:
        vk = _vk_from_char(s)
        if vk == 0:
            print("Unbekannte Taste. Lernmodus wird verwendet.")
            learn_key()
        else:
            VK_KEY = vk
            SC_KEY = _sc_from_vk(VK_KEY)
            print(f">> Taste gesetzt: VK=0x{VK_KEY:02X}, SC=0x{SC_KEY:02X}")
    else:
        learn_key()

def find_window_by_title_substring(sub: str):
    items = list_windows()
    sub = sub.lower()
    for hwnd, title in items:
        if sub in title.lower():
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            print(f"Automatisch ausgewählt: {title} (PID {pid})")
            return hwnd, title, pid
    return None, "", None

def learn_key():
    """Taste per tatsächlichem Tastendruck lernen (ScanCode)."""
    global VK_KEY, SC_KEY
    print(">> Lernmodus: Drücke jetzt EINMAL die gewünschte Taste ...")
    ev = keyboard.read_event(suppress=False)
    while ev.event_type != "down":
        ev = keyboard.read_event(suppress=False)
    SC_KEY = ev.scan_code & 0xFF
    try:
        if ev.name and len(ev.name) == 1:
            VK_KEY = ord(ev.name.upper())
        else:
            VK_KEY = 0
    except:
        VK_KEY = 0
    print(f">> Gelernt: SC=0x{SC_KEY:02X}  (VK=0x{VK_KEY:02X} – kann 0 sein, ist ok)")

# ====== Senden ======
def send_scancode(sc, up=False):
    flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if up else 0)
    inp = INPUT(type=INPUT_KEYBOARD, union=INPUTUNION(
        ki=KEYBDINPUT(wVk=0, wScan=sc, dwFlags=flags, time=0, dwExtraInfo=0)))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def send_vk(vk, up=False):
    flags = KEYEVENTF_KEYUP if up else 0
    inp = INPUT(type=INPUT_KEYBOARD, union=INPUTUNION(
        ki=KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)))
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def press_once():
    send_scancode(SC_KEY, up=False)
    time.sleep(HOLD_TIME)
    send_scancode(SC_KEY, up=True)
    if VK_KEY:
        time.sleep(0.01)
        send_vk(VK_KEY, up=False)
        time.sleep(0.01)
        send_vk(VK_KEY, up=True)

def click_mouse_once():
    """Führt einen Mausklick aus. Koordinaten optional setzen via MOUSE_X/MOUSE_Y."""
    global MOUSE_X, MOUSE_Y, MOUSE_BUTTON
    # Move cursor if coordinates provided
    try:
        if MOUSE_X is not None and MOUSE_Y is not None:
            win32api.SetCursorPos((int(MOUSE_X), int(MOUSE_Y)))
    except Exception:
        pass

    if MOUSE_BUTTON == "left":
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(HOLD_TIME)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif MOUSE_BUTTON == "right":
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(HOLD_TIME)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    elif MOUSE_BUTTON == "middle":
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
        time.sleep(HOLD_TIME)
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)

def click_mouse_double():
    click_mouse_once()
    time.sleep(0.06)
    click_mouse_once()

# ====== Fenster-Handling ======
def list_windows():
    wins = []
    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd): return
        t = win32gui.GetWindowText(hwnd) or ""
        if not t.strip(): return
        try:
            l,t2,r,b = win32gui.GetWindowRect(hwnd)
            if (r-l) < 150 or (b-t2) < 100: return
        except: return
        wins.append((hwnd, t.strip()))
    win32gui.EnumWindows(enum_handler, None)
    uniq = {}
    for h, t in wins: uniq.setdefault(t, h)
    return sorted([(h, t) for t, h in uniq.items()], key=lambda x: x[1].lower())

def pick_window():
    # Loop so the user can refresh the list if desired
    while True:
        items = list_windows()
        if not items:
            print("Keine sichtbaren Fenster gefunden.")
            return None, "", None
        print("\nWähle ein Fenster (Zahl + Enter) — oder 'r' zum Aktualisieren, 'q' zum Abbrechen:")
        for i, (hwnd, title) in enumerate(items):
            print(f"{i:2d}: {title}")
        s = input("> ").strip()
        if not s:
            print("Ungültig. Zahl oder 'r'/'q' eingeben.")
            continue
        if s.lower() == 'r':
            # refresh and show the list again
            continue
        if s.lower() == 'q':
            print("Abbruch.")
            return None, "", None
        try:
            idx = int(s)
            if 0 <= idx < len(items):
                hwnd, title = items[idx]
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                print(f"Ausgewählt: {title} (PID {pid})")
                return hwnd, title, pid
        except ValueError:
            pass
        print("Ungültig. Zahl aus Liste wählen oder 'r' zum Aktualisieren.")

def get_thread_id(hwnd):
    pid = ctypes.c_ulong()
    tid = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return tid

def get_foreground_hwnd():
    return user32.GetForegroundWindow()

def set_fg(hwnd):
    user32.BringWindowToTop(hwnd)
    user32.ShowWindow(hwnd, 8)  # SW_SHOWNA
    user32.SetForegroundWindow(hwnd)
    user32.SetActiveWindow(hwnd)
    user32.SetFocus(hwnd)

def press_with_stealth(target_hwnd):
    """kurz Fokus holen -> drücken -> Fokus zurück"""
    prev = get_foreground_hwnd()
    cur_tid = kernel32.GetCurrentThreadId()
    tgt_tid = get_thread_id(target_hwnd)
    prev_tid = get_thread_id(prev) if prev else 0

    send_vk(0x12, up=False); send_vk(0x12, up=True)  # VK_MENU

    user32.AttachThreadInput(cur_tid, tgt_tid, True)
    if prev: user32.AttachThreadInput(cur_tid, prev_tid, True)
    try:
        set_fg(target_hwnd)
        time.sleep(0.03)
        press_once()
        time.sleep(0.02)
        if prev and win32gui.IsWindow(prev):
            set_fg(prev)
    finally:
        user32.AttachThreadInput(cur_tid, tgt_tid, False)
        if prev: user32.AttachThreadInput(cur_tid, prev_tid, False)

def post_message_key(hwnd):
    scan = SC_KEY & 0xFF
    lparam_down = (1 | (scan << 16))
    lparam_up   = lparam_down | (1 << 30) | (1 << 31)
    user32.PostMessageW(hwnd, win32con.WM_KEYDOWN, VK_KEY or 0, lparam_down)
    time.sleep(HOLD_TIME)
    user32.PostMessageW(hwnd, win32con.WM_KEYUP,   VK_KEY or 0, lparam_up)

# ====== States / Loop ======
spamming = False
running = True
target_hwnd = None
target_title = ""
target_pid = None

def loop():
    print("Hotkeys: F9 Start/Stop | F8 Fenster wählen | F6 Stealth an/aus | F7 Debug | F4 Intervall | F3 Taste | F10 Stop | F12 Beenden")
    next_tick = time.time()
    while running:
        now = time.time()
        if spamming and now >= next_tick and target_hwnd and win32gui.IsWindow(target_hwnd):
            next_tick = now + INTERVAL
            # Mouse or key action
            if MOUSE_ENABLED:
                if DEBUG: print(f"[DBG] Mouse click ({MOUSE_BUTTON}) at {MOUSE_X},{MOUSE_Y}")
                if MOUSE_DOUBLE:
                    click_mouse_double()
                else:
                    click_mouse_once()
            else:
                if STEALTH_ON:
                    if DEBUG: print(f"[DBG] Stealth press (VK=0x{VK_KEY:02X}, SC=0x{SC_KEY:02X}, hold={HOLD_TIME}s)")
                    press_with_stealth(target_hwnd)
                else:
                    if DEBUG: print("[DBG] PostMessage press (Hintergrund)")
                    post_message_key(target_hwnd)
        time.sleep(0.005)

def toggle():
    global spamming
    if not target_hwnd:
        print("Kein Ziel-Fenster gewählt. F8 drücken."); return
    spamming = not spamming
    print(f"{'▶' if spamming else '■'} Auto-Key (alle {INTERVAL}s) – Ziel: {target_title} | Taste VK=0x{VK_KEY:02X}/SC=0x{SC_KEY:02X} | Stealth={'AN' if STEALTH_ON else 'AUS'}")

def stop():
    global spamming
    spamming = False
    print("Auto-Key: AUS")

def exit_app():
    global running, spamming
    spamming = False
    running = False
    print("Beenden...")

def choose_win():
    global target_hwnd, target_title, target_pid, spamming
    spamming = False
    target_hwnd, target_title, target_pid = pick_window()

def toggle_stealth():
    global STEALTH_ON
    STEALTH_ON = not STEALTH_ON
    print(f"Stealth-Fokus: {'AN' if STEALTH_ON else 'AUS'}")

def toggle_debug():
    global DEBUG
    DEBUG = not DEBUG
    print(f"Debug: {'AN' if DEBUG else 'AUS'}")

def change_interval():
    global INTERVAL
    try:
        s = input(f"Neues Intervall (Sekunden, aktuell {INTERVAL}): ").strip()
        if s:
            val = float(s.replace(",", "."))
            if val > 0:
                INTERVAL = val
                print(f">> Intervall gesetzt auf {INTERVAL} s")
            else:
                print("Intervall muss > 0 sein.")
    except:
        print("Ungültiger Wert.")

def change_key():
    configure_key_interactive()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto key presser (Windows).")
    parser.add_argument("--interval", type=float, help="Intervall in Sekunden")
    parser.add_argument("--key", type=str, help="Taste (z.B. g oder F5)")
    parser.add_argument("--title", type=str, help="Teil des Fenstertitels zum automatischen Auswählen")
    parser.add_argument("--index", type=int, help="Fenster-Index aus der Liste (0-bas.)")
    parser.add_argument("--noninteractive", action="store_true", help="Keine interaktiven Eingaben, nur CLI-Optionen verwenden")
    parser.add_argument("--stealth", type=str, choices=["on","off"], help="Stealth-Fokus an/aus")
    parser.add_argument("--debug", action="store_true", help="Debug-Ausgaben aktivieren")
    parser.add_argument("--mouse", action="store_true", help="Mausklick statt Tastendruck aktivieren")
    parser.add_argument("--mouse-button", type=str, choices=["left","right","middle"], default="left", help="Mausknopf")
    parser.add_argument("--mouse-x", type=int, help="X-Koordinate für Mausklick (optional)")
    parser.add_argument("--mouse-y", type=int, help="Y-Koordinate für Mausklick (optional)")
    parser.add_argument("--mouse-double", action="store_true", help="Doppelklick statt Einzelklick")
    args = parser.parse_args()

# Start-Überschrift
print("\n===========================================================================================================================")

print(r"""
  ___________           .__                       _____          __                  .__  .__        __                 
 /   _____/  | _________|__| _______  ______     /  _  \  __ ___/  |_  ____     ____ |  | |__| ____ |  | __ ___________ 
 \_____  \|  |/ /\_  __ \  |/ __ \  \/ /  _ \   /  /_\  \|  |  \   __\/  _ \  _/ ___\|  | |  |/ ___\|  |/ // __ \_  __ \
 /        \    <  |  | \/  \  ___/\   (  <_> ) /    |    \  |  /|  | (  <_> ) \  \___|  |_|  \  \___|    <\  ___/|  | \/
/_______  /__|_ \ |__|  |__|\___  >\_/ \____/  \____|__  /____/ |__|  \____/   \___  >____/__|\___  >__|_ \\___  >__|   
        \/     \/               \/                     \/                          \/             \/     \/    \/       
""")

print("============================================================================================================================\n")

# Logging
logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format="[%(levelname)s] %(message)s")
if args.debug:
    DEBUG = True

if args.interval and args.interval > 0:
    INTERVAL = args.interval

if args.stealth:
    STEALTH_ON = (args.stealth == "on")

# Key from CLI
if args.key:
    vk = _vk_from_char(args.key)
    if vk:
        VK_KEY = vk
        SC_KEY = _sc_from_vk(VK_KEY)
    else:
        # try to learn single-character
        VK_KEY = _vk_from_char(args.key)
        SC_KEY = _sc_from_vk(VK_KEY)

# Choose target window via CLI if requested
if args.noninteractive:
    if args.title:
        target_hwnd, target_title, target_pid = find_window_by_title_substring(args.title)
    elif args.index is not None:
        items = list_windows()
        if 0 <= args.index < len(items):
            target_hwnd, target_title = items[args.index]
            _, target_pid = win32process.GetWindowThreadProcessId(target_hwnd)
            logging.info(f"Ausgewähltes Fenster: {target_title} (PID {target_pid})")
    else:
        logging.error("--noninteractive verwendet, aber weder --title noch --index angegeben. Abbruch.")
        sys.exit(1)
else:
    # interactive default behavior
    target_hwnd, target_title, target_pid = pick_window()
    configure_key_interactive()

# Mouse CLI options
if args.mouse:
    MOUSE_ENABLED = True
    MOUSE_BUTTON = args.mouse_button
    if args.mouse_x is not None and args.mouse_y is not None:
        MOUSE_X = args.mouse_x
        MOUSE_Y = args.mouse_y
    MOUSE_DOUBLE = bool(args.mouse_double)

# Hotkeys (still useful)
keyboard.add_hotkey('F9', toggle)
keyboard.add_hotkey('F10', stop)
keyboard.add_hotkey('F12', exit_app)
keyboard.add_hotkey('F8', choose_win)
keyboard.add_hotkey('F6', toggle_stealth)
keyboard.add_hotkey('F7', toggle_debug)
keyboard.add_hotkey('F4', change_interval)
keyboard.add_hotkey('F3', change_key)

# Graceful shutdown on Ctrl+C
def _sigint_handler(signum, frame):
    logging.info("SIGINT empfangen, beende...")
    exit_app()
signal.signal(signal.SIGINT, _sigint_handler)

t = threading.Thread(target=loop, daemon=True)
t.start()

# Wait until exit_app sets running=False; keyboard.wait provides a simple blocking mechanism too
try:
    keyboard.wait('F12')
except KeyboardInterrupt:
    exit_app()
    
