import os
import re
from functools import cache, cached_property

import requests
from bs4 import BeautifulSoup
from utils import JSONFile, Log

log = Log('NameTranslator')


class NameTranslator:
    URL_SOURCE = 'https://dh-web.org/place.names/bot2sinhala.html'
    JSON_PATH = os.path.join('data', 'name_translations.json')

    def cleanup(self):
        if self.json_file.exists:
            os.remove(NameTranslator.JSON_PATH)
            log.warn(f'Removed {NameTranslator.JSON_PATH}')

    @staticmethod
    def extract_text(elem):
        return elem.text.strip().split('\n')[0].strip()

    @staticmethod
    def parse_scientific_name(elem):
        x = elem.text
        x = re.sub(r'[^a-zA-Z ]', ' ', x)
        x = re.sub(r'\s+', ' ', x)

        tokens = x.strip().split(' ')
        if len(tokens) < 2:
            return None

        genus, species = tokens[:2]
        scientific_name = ' '.join([genus.title(), species.lower()])
        return scientific_name

    def idx_no_cache(self):
        html = requests.get(NameTranslator.URL_SOURCE).text
        soup = BeautifulSoup(html, 'html.parser')

        idx = {}
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                columns = row.find_all('td')
                if len(columns) != 5:
                    continue

                scientific_name = NameTranslator.parse_scientific_name(
                    columns[0]
                )
                if not scientific_name:
                    continue
                sinhala = NameTranslator.extract_text(columns[1])
                pali_sanskrit = NameTranslator.extract_text(columns[2])
                tamil = NameTranslator.extract_text(columns[3])

                idx[scientific_name] = dict(
                    sinhala=sinhala,
                    pali_sanskrit=pali_sanskrit,
                    tamil=tamil,
                )
        return idx

    @property
    def json_file(self):
        return JSONFile(NameTranslator.JSON_PATH)

    @cached_property
    def idx(self):
        if not self.json_file.exists:
            idx = self.idx_no_cache()
            self.json_file.write(idx)
            log.info(
                f'Wrote {len(idx)} name translations to {NameTranslator.JSON_PATH}'
            )
        return self.json_file.read()

    @cache
    def get(self, scientific_name):
        return self.idx.get(scientific_name, None)
