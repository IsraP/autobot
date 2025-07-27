import shutil
from bs4 import BeautifulSoup
from constants import BASE_URL, DUMP_LEADS_FILE
from utils import clear_screen, get_key
from interactions import fetch_interactions, send_interaction


# ─ Fetch Leads ─────────────────────────────────────────────────────────────────
def fetch_leads(session, page):
    url = f"{BASE_URL}/Lead/ObterleadsAjax"
    params = {'status':1,'midia':0,'page':page,'usuario':0,'buscarapida':'','ordenacao':0}
    r = session.get(url, params=params)
    try:
        data = r.json()
        leads = data if isinstance(data, list) else data.get('dados', [])
        if leads:
            return leads
    except ValueError:
        pass
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    leads = []
    container = soup.find('div', class_='inbox-content')
    if not container:
        DUMP_LEADS_FILE.write_text(html, encoding='utf-8')
        print(f"⚠️ No leads found. HTML dumped to {DUMP_LEADS_FILE}")
        return []
    for a in container.find_all('a', class_='loadPageAjax'):
        div = a.find('div', attrs={'data-id': True})
        lead_id = div['data-id']
        name = div.find('span', class_='nomeClienteLead').get_text(strip=True)
        car = a.find('div', class_='VersaoVeiculoLead').get_text(strip=True)
        date = a.find('span', class_='dataLead').get_text(strip=True)
        leads.append({'Id': lead_id,'ClienteNome': name,'Veiculo': car,'DataCadastro': date})
    if not leads:
        DUMP_LEADS_FILE.write_text(html, encoding='utf-8')
        print(f"⚠️ No leads parsed. HTML dumped to {DUMP_LEADS_FILE}")
    return leads






# ─ Interactive Lead Navigation ─────────────────────────────────────────────────
def navigate_leads(session):
    page = 1
    idx = 0
    leads = fetch_leads(session, page)

    def load(page_num):
        clear_screen()
        print(f"Loading page {page_num}...")
        return fetch_leads(session, page_num)

    while True:
        clear_screen()
        print(f"Leads - Page {page}")
        if not leads:
            print("(no leads to display)")
        else:
            for i, lead in enumerate(leads):
                prefix = '>' if i == idx else ' '
                print(f"{prefix} {lead['ClienteNome']} | {lead['Veiculo']} | {lead['DataCadastro']}")
        key = get_key()
        if key == 'LEFT' and page > 1:
            page -= 1; idx = 0; leads = load(page)
        elif key == 'RIGHT':
            page += 1; idx = 0; leads = load(page)
        elif key == 'UP' and idx > 0:
            idx -= 1
        elif key == 'DOWN' and idx < len(leads) - 1:
            idx += 1
        elif key == 'ENTER' and leads:
            lead = leads[idx]
            interactions = fetch_interactions(session, lead['Id'])
            clear_screen()
            term_width = shutil.get_terminal_size((80, 20)).columns
            print(f"Interactions for Lead {lead['ClienteNome']} (ID {lead['Id']})")
            for inter in interactions:
                if inter['type'] == 'client':
                    label = f"Client [{inter['time']}]"
                    print(label)
                    for line in inter['text'].split('\n'):
                        print(line)
                    print()
                else:
                    author = inter.get('author', 'Store')
                    label = f"{author} [{inter['time']}]"
                    print(label.rjust(term_width))
                    for line in inter['text'].split('\n'):
                        print(line.rjust(term_width))
                    print()
            choice = input("\n(V)iew again, (S)end message, or (B)ack: ").strip().lower()
            if choice == 's':
                msg = input('Enter your message: ').strip()
                while True:
                    resp = send_interaction(session, lead['Id'], msg)
                    if resp.get('Success'):
                        print(f"✅ Sent: {resp.get('Message')}")
                        break
                    else:
                        print(f"❌ Failed: {resp.get('Message')}")
                        retry = input('Retry? (y/N): ').strip().lower()
                        if retry not in ('y','yes'):
                            break
                input('Press any key to refresh conversation...')
            leads = load(page)
            idx = 0
        elif key == 'QUIT':
            break