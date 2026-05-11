"""Windows-native WeChat Desktop controller using Win32 API and SendInput.

This module must run on Windows (not WSL). Use cmd.exe /c to invoke.
"""
import ctypes
from ctypes import wintypes
import time
import struct

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Virtual key codes
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_F = 0x46
VK_V = 0x56

# Input type constants
INPUT_KEYBOARD = 1

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUT),
    ]

KEYEVENTF_KEYUP = 0x0002

def send_key(vk_code, press=True):
    """Send a single key press or release."""
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk_code
    inp.union.ki.dwFlags = 0 if press else KEYEVENTF_KEYUP
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def key_combination(*keys):
    """Press a combination of keys, then release in reverse order."""
    for k in keys:
        send_key(k, True)
        time.sleep(0.05)
    for k in reversed(keys):
        send_key(k, False)
        time.sleep(0.05)

def press_key(vk_code):
    """Press and release a single key."""
    send_key(vk_code, True)
    time.sleep(0.05)
    send_key(vk_code, False)
    time.sleep(0.05)

def type_text(text):
    """Type text by putting it on clipboard and pasting (Ctrl+V)."""
    # Use SendKeys directly - more reliable than clipboard for WeChat
    _type_via_keys(text)

def _type_via_keys(text):
    """Fallback: type text character by character via key events."""
    for char in text:
        # Convert char to virtual key code
        vk = ctypes.windll.user32.VkKeyScanW(ord(char))
        if vk != -1:
            vk_code = vk & 0xFF
            shift = (vk >> 8) & 1
            if shift:
                send_key(0x10, True)  # Shift down
            send_key(vk_code, True)
            time.sleep(0.02)
            send_key(vk_code, False)
            if shift:
                send_key(0x10, False)  # Shift up
        time.sleep(0.03)

def find_wechat_window():
    """Find all WeChat/Weixin windows."""
    windows = []
    def enum_proc(hwnd, _):
        length = user32.GetWindowTextLengthW(hwnd) + 1
        title = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, title, length)
        
        class_name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_name, 256)
        
        t = title.value
        if t in ("微信", "Weixin") and "Qt5" in class_name.value:
            windows.append(hwnd)
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_proc), 0)
    return windows

def activate_wechat():
    """Bring WeChat window to foreground."""
    wins = find_wechat_window()
    if not wins:
        return False, "WeChat window not found"
    
    hwnd = wins[0]
    user32.ShowWindow(hwnd, 1)  # SW_SHOWNORMAL
    time.sleep(0.2)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    return True, f"Activated WeChat (HWND={hwnd:#x})"

def search_contact(name):
    """Search for a contact by name and open their chat."""
    ok, msg = activate_wechat()
    if not ok:
        return ok, msg
    
    # Ctrl+F to open search
    key_combination(VK_CONTROL, VK_F)
    time.sleep(0.5)
    
    # Type contact name
    type_text(name)
    time.sleep(0.5)
    
    # Press Enter to open first result
    press_key(VK_RETURN)
    time.sleep(0.5)
    
    return True, f"Searched for '{name}'"

def send_message(contact, message):
    """Send a message to a WeChat contact."""
    ok, msg = search_contact(contact)
    if not ok:
        return ok, msg
    
    # Type the message via clipboard
    type_text(message)
    time.sleep(0.3)
    
    # Ctrl+Enter or just Enter to send (WeChat uses Enter by default)
    press_key(VK_RETURN)
    time.sleep(0.3)
    
    return True, f"Message sent to '{contact}': {message[:30]}..."

def get_status():
    """Check WeChat status."""
    wins = find_wechat_window()
    if not wins:
        return {"running": False, "windows": 0}
    
    hwnd = wins[0]
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    
    is_visible = user32.IsWindowVisible(hwnd)
    is_minimized = user32.IsIconic(hwnd)
    
    title = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, title, 256)
    
    return {
        "running": True,
        "windows": len(wins),
        "title": title.value,
        "visible": bool(is_visible),
        "minimized": bool(is_minimized),
        "bounds": {
            "left": rect.left, "top": rect.top,
            "right": rect.right, "bottom": rect.bottom
        }
    }
