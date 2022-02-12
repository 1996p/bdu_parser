import requests
from bs4 import BeautifulSoup
import json
import os
import threading


class Parser(threading.Thread):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    URL = 'https://bdu.fstec.ru/threat'
    TEMPLATE_URL = 'https://bdu.fstec.ru/threat/ubi.'

    def __init__(self, threats_list, threat_number, lock, *args, **kwargs):
        super(Parser, self).__init__(*args, **kwargs)
        self.qty_of_elements = 0
        self.threats = threats_list
        self.threat_number = threat_number
        self.lock = lock

    def run(self):
        if self.threat_number < 10:
            threat_number = f'00{self.threat_number}'
        elif self.threat_number < 100:
            threat_number = f'0{self.threat_number}'
        else:
            threat_number = str(self.threat_number)

        threat_url = self.TEMPLATE_URL + threat_number
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
        with self.lock:
            self.threats.append(data_dict)

    @classmethod
    def get_qty_elements(cls):
        q = requests.get(url=cls.URL, headers=cls.HEADERS)
        soup = BeautifulSoup(q.text, 'lxml')
        qty_of_elements = int(soup.find('div', class_='summary').text.split()[-1])
        return qty_of_elements


if __name__ == '__main__':
    threats = []
    threat_count = Parser.get_qty_elements()

    lock = threading.Lock()
    parsers = [Parser(threats_list=threats, threat_number=i, lock=lock) for i in range(1, threat_count + 1)]

    for parser in parsers:
        parser.start()

    print('Threads were started, now just waitin...')

    for parser in parsers:
        parser.join()

    if not os.path.exists(os.curdir + '/data'):
        os.mkdir(os.curdir + '/data')
        print('Folder for data was created!')

    with open('data/threats.json', 'w', encoding='utf-8') as file:
        json.dump(threats, file, indent=4, ensure_ascii=False)


