from bs4 import BeautifulSoup
from datetime import datetime
from constants import BASE_URL

# ─ Fetch Interactions ────────────────────────────────────────────────────────────
def fetch_interactions(session, lead_id):
    url = f"{BASE_URL}/Lead/ObterInteracoesAjax"
    r = session.get(url, params={'id': lead_id})
    soup = BeautifulSoup(r.extract_text, 'html.parser')

    interactions = []
    current_date = None

    # grab everything in the order it appears: date headers, then client/store messages
    for el in soup.select('div.chat-line, div.interacaoClienteMessenger, div.interacaoLojaMessenger'):
        classes = el.get('class', [])

        # date header
        if 'chat-line' in classes:
            date_text = el.find('span', class_='chat-date').get_text(strip=True)
            try:
                current_date = datetime.strptime(date_text, '%d/%m/%Y').date()
            except ValueError:
                current_date = None

        # client message
        elif 'interacaoClienteMessenger' in classes:
            text = el.find('div', class_='interacaoTeor').get_text(strip=True)
            time_str = el.find('div', class_='interacaoHorario').get_text(strip=True)
            interactions.append({
                'type': 'client',
                'text': text,
                'time': time_str,
                'date': current_date
            })

        # store message
        elif 'interacaoLojaMessenger' in classes:
            text = el.find('div', class_='interacaoTeor').get_text(strip=True)
            time_str = el.find('div', class_='interacaoHorario').get_text(strip=True)
            author_tag = el.find('div', style=lambda v: v and 'Feito por' in v)
            author = author_tag.get_text(strip=True) if author_tag else 'Store'
            interactions.append({
                'type': 'store',
                'text': text,
                'time': time_str,
                'author': author,
                'date': current_date
            })

    # build timestamps so you can optionally sort/fallback if needed
    for inter in interactions:
        dt_obj = None

        if inter['date'] and inter.get('time'):
            dt_str = f"{inter['date']} {inter['time']}"
            try:
                dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            except ValueError:
                dt_obj = None
        inter['timestamp'] = dt_obj


    return interactions


# ─ Send Interaction ────────────────────────────────────────────────────────────
def send_interaction(session, lead_id, message):
    url = f"{BASE_URL}/Lead/SalvarInteracao"
    payload = {'Id': lead_id, 'Value': message}
    r = session.post(url, json=payload)
    try:
        return r.json()
    except ValueError:
        return {'Success': False, 'Message': 'Invalid response'}