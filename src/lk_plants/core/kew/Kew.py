import os
import time
from functools import cached_property

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from utils import Log, JSONFile

log = Log('Kew')


class Kew:
    DIR_DATA_KEW = os.path.join(
        'data',
        'kew',
    )
    def __init__(self, powo_id: str):
        self.powo_id = powo_id

    @cached_property
    def url(self) -> str:
        return (
            'https://powo.science.kew.org/taxon/'
            + 'urn:lsid:ipni.org:names:'
            + self.powo_id
            + '#higher-classification'
        )

    @cached_property
    def file_path(self) -> str:
        if not os.path.exists(Kew.DIR_DATA_KEW):
            os.makedirs(Kew.DIR_DATA_KEW)
        return os.path.join(
            Kew.DIR_DATA_KEW,
            f'{self.powo_id}.json',
        )
    @cached_property
    def classification_nocache(self) -> dict:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options)

        log.debug(f'Opening {self.url}...')
        driver.get(self.url)
        time.sleep(1)

        elem_ul = driver.find_element(
            By.XPATH, "//ul[@class='c-classification-list']"
        )
        d = {}
        for elem_li in elem_ul.find_elements(By.XPATH, ".//li"):
            elem_span_list = elem_li.find_elements(By.XPATH, ".//span")
            key = elem_span_list[0].text
            value = elem_span_list[1].text
            d[key] = value

        driver.quit()

        return d

    @cached_property
    def data(self) -> dict:
        if os.path.exists(self.file_path):
            return JSONFile(self.file_path).read()
        
        classification = self.classification_nocache
        data = dict(
            powo_id=self.powo_id,
            classification=classification,
        )
        JSONFile(self.file_path).write(data)
        log.info(f'Wrote {self.file_path}')
        return data