import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Função para rolar até o final da página
def scroll_to_bottom(driver, max_clicks=3):
    for _ in range(max_clicks):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

# Função para raspar os eventos
def scrape_events(driver, url, selectors):
    driver.get(url)
    driver.implicitly_wait(30)
    scroll_to_bottom(driver)

    page_content = driver.page_source
    webpage = BeautifulSoup(page_content, 'html.parser')

    events = webpage.find_all(selectors['event']['tag'], class_=selectors['event'].get('class'))
    event_list = []

    for event in events:
        event_info = {}
        for key, selector in selectors.items():
            if key != 'event':
                element = event.find(selector['tag'], class_=selector.get('class'))
                event_info[key] = element.text.strip() if element else None
                if key == 'Image URL':
                    event_info[key] = element['src'] if element and 'src' in element.attrs else None

        # Clique no link do evento para acessar a página detalhada
        event_link = event.find('a', href=True)['href']
        driver.get(event_link)

        # Aguarde até que a página detalhada seja carregada completamente
        time.sleep(3)

        # Raspe informações detalhadas da página do evento
        event_page_content = driver.page_source
        event_page = BeautifulSoup(event_page_content, 'html.parser')

        # Modifique esta parte de acordo com a estrutura específica da página do evento
        # Exemplo: extrair informações do título, data, local e descrição
        title = event_page.find('h1', class_='event-title css-0').text.strip() if event_page.find('h1', class_='event-title css-0') else None
        description = event_page.find('p', class_='summary').text.strip() if event_page.find('p', class_='summary') else None
        price = event_page.find('div', class_='conversion-bar__panel-info').text.strip() if event_page.find('div', class_='conversion-bar__panel-info') else None
        date = event_page.find('span', class_='date-info__full-datetime').text.strip() if event_page.find('span', class_='date-info__full-datetime') else None
        location = event_page.find('p', class_='location-info__address-text').text.strip() if event_page.find('p', class_='location-info__address-text') else None

        # Adicionar as informações detalhadas ao dicionário de informações do evento
        event_info['Title'] = title
        event_info['Description'] = description
        event_info['Price'] = price
        event_info['Date'] = date
        event_info['Location'] = location

        event_list.append(event_info)

        # Navegar de volta para a página inicial de eventos para continuar a raspagem
        driver.get(url)

    return event_list

def main():
    sources = [
        {
            'name': 'Eventbrite',
            'url': 'https://www.eventbrite.com/d/canada--montreal/all-events/',
            'selectors': {
                'event': {'tag': 'div', 'class': 'discover-search-desktop-card discover-search-desktop-card--hiddeable'},
                'Date': {'tag': 'p', 'class': 'Typography_root__487rx #585163 Typography_body-md__487rx event-card__clamp-line--one Typography_align-match-parent__487rx'},
                'Location': {'tag': 'p', 'class': 'Typography_root__487rx #585163 Typography_body-md__487rx event-card__clamp-line--one Typography_align-match-parent__487rx'},
                'Price': {'tag': 'p', 'class': 'Typography_root__487rx #3a3247 Typography_body-md-bold__487rx Typography_align-match-parent__487rx'},
                'Image URL': {'tag': 'img', 'class': 'event-card-image'}
            },
        }
    ]

    all_events = []

    for source in sources:
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        events = scrape_events(driver, source['url'], source['selectors'])
        driver.quit()

        source_data = {
            'source_name': source['name'],
            'events': events
        }

        all_events.append(source_data)

    file_name = "events_data.json"  # Nome do arquivo JSON a ser criado

    with open(file_name, "w") as json_file:
        json.dump(all_events, json_file, indent=2)

    print(f"Os dados JSON foram gravados em {file_name}")

    # Carregar o arquivo JSON
    with open(file_name, 'r') as file:
        data = json.load(file)

    # Imprimir o conteúdo do arquivo JSON no terminal
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
