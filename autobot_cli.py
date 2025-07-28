#!/usr/bin/env python3
import argparse
from pyfiglet import figlet_format
from session import get_api_session, parse_arguments
from leads import navigate_leads

# ─ Main CLI Flow ────────────────────────────────────────────────────────────────
def main():
    args = parse_arguments()

    print(figlet_format('autovendedor', font='slant'))

    session = get_api_session(args)

    print("\nUse arrow keys to browse leads, Enter to select, Ctrl+Z or 'q' to quit.")
    navigate_leads(session)

if __name__ == '__main__':
    main()
