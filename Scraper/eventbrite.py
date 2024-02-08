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

# Função para extrair informações detalhadas da página do evento
def scrape_event_details(event_page, selectors):
    event_info = {}
    for key, selector in selectors.items():
        if key != 'event':
            element = event_page.find(selector['tag'], class_=selector.get('class'))
            event_info[key] = element.text.strip() if element else None
            if key == 'Image URL':
                event_info[key] = element['src'] if element and 'src' in element.attrs else None
    return event_info

# Função para raspar os eventos em uma página
def scrape_events_on_page(driver, url, selectors, max_events_per_page=10):
    driver.get(url)
    driver.implicitly_wait(30)

    all_events = []

    for _ in range(max_events_per_page):
        page_content = driver.page_source
        webpage = BeautifulSoup(page_content, 'html.parser')
        events = webpage.find_all(selectors['event']['tag'], class_=selectors['event'].get('class'))

        for event in events:
            event_info = scrape_event_details(event, selectors)
            event_link = event.find('a', href=True)['href']

            driver.get(event_link)
            time.sleep(3)

            event_page_content = driver.page_source
            event_page = BeautifulSoup(event_page_content, 'html.parser')
            tags_container = event_page.find('ul', class_=selectors['Tags'].get('class'))
            event_info['Tags'] = [tag.text.strip() for tag in tags_container.find_all('a')] if tags_container else None

            all_events.append(event_info)
            driver.back()
            time.sleep(3)

    return all_events

# Função principal
def main():
    sources = [
        {
            'name': 'Eventbrite',
            'url': 'https://www.eventbrite.com/d/canada--montreal/all-events/',
            'selectors': {
                'event': {'tag': 'div', 'class': 'discover-search-desktop-card discover-search-desktop-card--hiddeable'},
                'Title': {'tag': 'h2', 'class': 'Typography_root__487rx #3a3247 Typography_body-lg__487rx event-card__clamp-line--two Typography_align-match-parent__487rx'},
                'Description': {'tag': 'p', 'class': 'summary'},
                'Date': {'tag': 'p', 'class': 'Typography_root__487rx #585163 Typography_body-md__487rx event-card__clamp-line--one Typography_align-match-parent__487rx'},
                'Location': {'tag': 'p', 'class': 'Typography_root__487rx #585163 Typography_body-md__487rx event-card__clamp-line--one Typography_align-match-parent__487rx'},
                'Price': {'tag': 'p', 'class': 'Typography_root__487rx #3a3247 Typography_body-md-bold__487rx Typography_align-match-parent__487rx'},
                'Image URL': {'tag': 'img', 'class': 'event-card-image'},
                'Tags': {'tag': 'ul', 'class': 'your-ul-class-here'},
                'Organizer': {'tag': 'a', 'class': 'descriptive-organizer-info__name-link'},
                'Image URL Organizer': {'tag': 'svg', 'class': 'eds-avatar__background eds-avatar__background--has-border'},
            },
        }
    ]

    all_events = []

    for source in sources:
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        events = scrape_events_on_page(driver, source['url'], source['selectors'], max_events_per_page=5)
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
