#!/usr/bin/env python3
import argparse
from pyfiglet import figlet_format
from session import create_new_session, create_api_session, load_session
from leads import navigate_leads

# ─ Main CLI Flow ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--headful', action='store_true', help='Run browser in headful mode')
    args = parser.parse_args()

    print(figlet_format('autobot', font='slant'))

    saved = load_session()
    if saved:
        cookies_dict = saved
        session = create_api_session(cookies_dict)
    else:
        session = create_new_session(args)

    print("\nUse arrow keys to browse leads, Enter to select, Ctrl+Z or 'q' to quit.")
    navigate_leads(session)

if __name__ == '__main__':
    main()
