import requests
from bs4 import BeautifulSoup
import json

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }


def get_qty_elements(url):
    q = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(q.text, 'lxml')
    qty_of_elements = int(soup.find('div', class_='summary').text.split()[-1])
    return qty_of_elements


def get_page(url):
    qty_threats = get_qty_elements(url=url)
    threat_url_template = 'https://bdu.fstec.ru/threat/ubi.'

    threats = []

    for i in range(1, qty_threats + 1):
        if i < 10:
            threat_number = f'00{i}'
        elif i < 100:
            threat_number = f'0{i}'
        else:
            threat_number = str(i)

        threat_url = threat_url_template + threat_number
        print(f'Go to {threat_url}..')
        q = requests.get(url=threat_url, headers=headers)
        soup = BeautifulSoup(q.text, 'lxml')

        container = soup.find('div', class_='container-fluid').find('div', class_='row')
        threat_name = container.find('h4').text
        table = container.find('table', class_='attr-view-table').find_all('tr')

        data_dict = {threat_name[:7]: threat_name[9:]}

        for parameter in table:
            parameter_info = parameter.find_all('td')
            data_dict[parameter_info[0].text.strip()] = parameter_info[1].text.strip().replace('\n', ',')

        threats.append(data_dict)
    with open('threats.json', 'w', encoding='utf-8') as file:
        json.dump(threats, file, indent=4, ensure_ascii=False)


def main():
    url = 'https://bdu.fstec.ru/threat'
    get_page(url=url)


if __name__ == '__main__':
    main()

