import msvcrt
import os

# ─ Terminal Helpers ─────────────────────────────────────────────────────────────
def clear_screen(): os.system('cls' if os.name=='nt' else 'clear')

def get_key():
    first = msvcrt.getch()
    if first == b'\x1a':
        return 'QUIT'
    if first == b'\xe0':
        second = msvcrt.getch()
        return {'H':'UP','P':'DOWN','K':'LEFT','M':'RIGHT'}.get(second.decode(), None)
    if first == b'\r':
        return 'ENTER'
    if first in (b'q', b'Q'):
        return 'QUIT'
    return None