import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from utils import Log

log = Log('scrape_app')


def main():
    
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    width = 2400
    height = width * 9 / 16
    driver.set_window_size(width, height)

    eppId = 'Photo-2024-03-08-07-14-47'
    URL = 'https://nuuuwan.github.io/plants/'+f'?activeEPPId={eppId}'
    driver.get(URL)
    time.sleep(3)

    image_path = os.path.join('images', 'app.png')
    driver.save_screenshot(image_path)
    log.info(f'Wrote {image_path}')
    driver.quit()


if __name__ == "__main__":
    main()
