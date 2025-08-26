#!/usr/bin/env python3
import argparse
from pyfiglet import figlet_format
from session import create_new_session, create_api_session, load_session
from leads import navigate_leads, extract_leads

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
    print('Escolha uma das opções:\n')
    print('1 - Navegar nos Leads\n')
    print('2 - Extrator\n')
    option = input('Selecione uma opção: ').strip()
    match(option):
        case '1':
            navigate_leads(session)
        case '2':
            extract_leads(session)
        case _:
            return None
    

if __name__ == '__main__':
    main()
