import pathlib

# ─ Configuration ────────────────────────────────────────────────────────────────
BASE_URL = "https://sistema.autocerto.com"
PROJECT_DIR = pathlib.Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_DIR / "lastSession.txt"
PROFILE_DIR = PROJECT_DIR / ".autobot_profile"
DUMP_LEADS_FILE = PROJECT_DIR / "dump.html"
DUMP_LOGIN_FILE = PROJECT_DIR / "dump_login.html"