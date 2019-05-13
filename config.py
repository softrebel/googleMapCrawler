import os
import logging

FORMAT = '%(asctime)-15s %(levelname)-9s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging.FileHandler('log.txt', 'a', 'utf-8')])

dir_path = os.path.dirname(os.path.realpath(__file__))

dbConfig = {
    'user': 'test',
    'password': 'test',
    'host': '127.0.0.1',
    'database': 'crawl',
    'raise_on_warnings': True
}

base_url = "https://www.google.com/maps/"

xpath_list = {
    'image': '//div[contains(@class,\"section-hero-header\")]/button/img',
    'title': '//*[contains(@class,"section-hero-header-title")]',
    'subtitle': '//*[contains(@class,"section-hero-header-subtitle")]',
    'category': '//*[contains(@jsaction,"pane.rating.category")]',
    'address_en': '(//*[contains(@aria-label,"Address")]'
                  '/parent::*//*[contains(@class,"section-info-text")]/span[contains(@class,"widget-pane-link")])[1]',
    'address_fa': '(//*[contains(@aria-label,"Address")]'
                  '/parent::*//*[contains(@class,"section-info-text")]/span[contains(@class,"widget-pane-link")])[2]',
    'phone': '//*[contains(@aria-label,"Phone")]'
             '/parent::*//*[contains(@class,"section-info-text")]/span[contains(@class,"widget-pane-link")]',
    'website': '//*[contains(@aria-label,"Website")]'
               '/parent::*//*[contains(@class,"section-info-text")]/span[contains(@class,"widget-pane-link")]',
    'hours': '//*[contains(@aria-label,"Hours")]'
             '/parent::*//span[contains(@class,"section-info-text")][2]',
    'score': '//*[contains(@class,"section-star-display")]',
}

# next_button_xpath = '//button[contains(@aria-label,"Next page")]'
next_button_xpath = '//*[contains(@class,"button-next-icon")]/parent::button'
prev_button_xpath = '//button[contains(@aria-label,"Previous page")]'

main_page_xpath = "section-back-to-list-button"
section_result_class = "section-result"
search_box_button_class = "searchbox-searchbutton"

sleep_scale = 1.5

search_input_default = 'استخر'
profileShahrestanID_default = 2624
profileShahrestanName_default = 'شیراز'

title_duplicate_xpath = '//h3[contains(@class,"section-result-title")]/span'
score_duplicate_xpath = '//*[contains(@class,"section-result-rating")]/span'

find_gps_point_service = 'http://api.sshb.local/v1/Locations/FindGPSPointInfo'

status_in_queue = 1
status_in_progress = 2
status_did_progress = 3
status_not_related_to_search = 4
