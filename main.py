import requests
from bs4 import BeautifulSoup as BS
from fake_headers import Headers
import time
import json

def get_links(text):
    headers_date = Headers(browser='firefox', os='win')
    headers = headers_date.generate()
    response = requests.get(
        url=f'https://hh.ru/search/vacancy?no_magic=true&L_save_area=true&text={text}&excluded_text=&area=2&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=50&page=0',
        headers= headers
    )
    if response.status_code != 200:
        return
    soup = BS(response.content, 'lxml')
    try:
        page_count = int(soup.find('div', attrs={'class':'pager'}).find_all('span', recursive=False)[-1].find('a').find('span').text)
    except:
        return
    for page in range(page_count):
        try:
            response = requests.get(
            url=f'https://hh.ru/search/vacancy?no_magic=true&L_save_area=true&text={text}&excluded_text=&area=2&area=1&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=50&page={page}',
            headers= headers
            )
            if response.status_code != 200:
                continue
            for a in soup.find_all('a', attrs={'class':'serp-item__title'}):
                yield f'{a.attrs["href"]}'
        except Exception as e:
            print(f'{e}')
        time.sleep(1)

def get_result(link):
    headers_date = Headers(browser='firefox', os='win')
    headers = headers_date.generate()
    response = requests.get(
        url=link,
        headers=headers
    )
    if response.status_code != 200:
        return
    soup = BS(response.content, 'lxml')
    try:
        title = soup.find(attrs={'class':'bloko-header-section-1'}).text
    except:
        title = ''
    try:
        salary = soup.find('span', attrs={'data-qa':'vacancy-serp__vacancy-compensation', 'class':'bloko-header-section-3'}).text.replace('\u202f', '')
    except:
        salary = 'Договорная'
    try:
        company = soup.find(attrs={'class':'bloko-link_kind-tertiary'}).text.replace("\xa0", " ")
    except:
        company = ''
    try:
        city = soup.find('p', attrs={'data-qa':'vacancy-view-location'}).text
    except:
        city = 'Не указано'
    try:
        description = soup.find('div', attrs={'class':'vacancy-branded-user-content'}).text
    except:
        description = ''
    result = {
        'Title':title,
        'Salary':salary,
        'Company':company,
        'City':city,
        'Description':description
    }
    return result
if __name__ == "__main__":
    data = []
    for l in get_links('python'):
        if 'Django' or 'Flask' in get_result(l)['Description']:
            vacancy = {}
            vacancy['Title'] = get_result(l)['Title']
            time.sleep(0.6)
            salary = {}
            salary['Salary'] = get_result(l)['Salary']
            vacancy.update(salary)
            time.sleep(0.6)
            company = {}
            company['Company'] = get_result(l)['Company']
            vacancy.update(company)
            time.sleep(0.6)
            city = {}
            city['City'] = get_result(l)['City']
            vacancy.update(city)
            data.append(vacancy)
            time.sleep(1)
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
