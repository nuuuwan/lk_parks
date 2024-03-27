import os
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from utils import Log

log = Log('App')


class App:
    @staticmethod
    def scrape():
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        width = 1600
        height = width * 9 / 16
        driver.set_window_size(width, height)

        eppId = 'Photo-2024-03-08-07-14-47'
        URL = 'https://nuuuwan.github.io/plants/' + f'?activeEPPId={eppId}'
        log.debug(f'Openning {URL}...')
        driver.get(URL)
        time.sleep(3)

        image_path = os.path.join('images', 'app.png')
        driver.save_screenshot(image_path)
        log.info(f'Wrote {image_path}')
        driver.quit()
