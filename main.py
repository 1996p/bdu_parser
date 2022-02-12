import requests
from bs4 import BeautifulSoup
import json
import os


class Parser:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    def __init__(self):
        self.url = 'https://bdu.fstec.ru/threat'
        self.template_url = 'https://bdu.fstec.ru/threat/ubi.'
        self.qty_of_elements = 0
        self.threats = []

    def get_qty_elements(self):
        q = requests.get(url=self.url, headers=self.HEADERS)
        soup = BeautifulSoup(q.text, 'lxml')
        self.qty_of_elements = int(soup.find('div', class_='summary').text.split()[-1])

    def run(self):
        self.get_qty_elements()

        for i in range(1, self.qty_of_elements + 1):
            if i < 10:
                threat_number = f'00{i}'
            elif i < 100:
                threat_number = f'0{i}'
            else:
                threat_number = str(i)

            threat_url = self.template_url + threat_number
            print(f'Go to {threat_url}..')

            response = requests.get(url=threat_url, headers=self.HEADERS)
            soup = BeautifulSoup(response.text, 'lxml')
            container = soup.find('div', class_='container-fluid').find('div', class_='row')
            threat_name = container.find('h4').text
            table = container.find('table', class_='attr-view-table').find_all('tr')

            data_dict = {threat_name[:7]: threat_name[9:]}

            for parameter in table:
                parameter_info = parameter.find_all('td')
                data_dict[parameter_info[0].text.strip()] = parameter_info[1].text.strip().replace('\n', ',')

            self.threats.append(data_dict)

        if not os.path.exists(os.curdir + '/data'):
            os.mkdir(os.curdir + '/data')
            print('Folder for data was created!')

        with open('data/threats.json', 'w', encoding='utf-8') as file:
            json.dump(self.threats, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    pars = Parser()
    pars.run()