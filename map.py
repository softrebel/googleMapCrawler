from config import *
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re, json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from crawlRepo import *


class mapCrawl():
    def __init__(self, category=None, profileShahrestanID=None, profileShahrestanName=None, crawler=None, url=None):
        self.section_list = []
        self.do_crawl = True
        self.repo = ''
        self.category = category if category else search_input_default  # profileGhalebSakhtarMajmooeh
        self.profileShahrestanID = profileShahrestanID if profileShahrestanID else profileShahrestanID_default  # profileShahrestan
        self.profileShahrestanName = profileShahrestanName if profileShahrestanName else profileShahrestanName_default  # profileShahrestan
        self.repo = crawler if crawler else crawlRepo()
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--lang=en')

        self.driver = webdriver.Chrome(executable_path=dir_path + os.sep + "chromedriver.exe",
                                       chrome_options=chrome_options)
        if url is None:
            self.driver.get(base_url)
        else:
            self.driver.get(url)


    def initial_search(self):
        search_box_input = WebDriverWait(self.driver, 2).until(self.find_search_box_input)
        search_box_button = self.driver.find_element(By.CLASS_NAME, search_box_button_class)
        # نام شهر و دسته بندی را جستجو میکنیم
        search_box_input.send_keys(self.profileShahrestanName + ' ' + self.category)
        search_box_button.click()

    def search_start_from_point(self, geo_point):
        search_box_input = WebDriverWait(self.driver, 2).until(self.find_search_box_input)
        search_box_button = self.driver.find_element(By.CLASS_NAME, search_box_button_class)
        # نام شهرستان را اول جستجو میکنیم
        search_box_input.send_keys(geo_point)
        search_box_button.click()
        self.set_sleep_scale(1.5)
        while True:
            if 'data' in self.driver.current_url:
                if search_box_button.is_enabled():
                    break
        search_box_input.clear()
        # نام دسته بندی را جستجو میکنیم
        search_box_input.send_keys(self.category)
        search_box_button.click()

    def find_section_result(self, driver):
        element = self.driver.find_elements(By.CLASS_NAME, section_result_class)
        if element:
            return element
        else:
            return False

    def find_search_box_input(self, driver):
        element = self.driver.find_element(By.ID, "searchboxinput")
        if element:
            return element
        else:
            return False

    def back_to_main_page(self):
        count = 0
        while True:
            try:
                back = self.driver.find_element_by_class_name(main_page_xpath)
                back.click()
                self.set_sleep_scale(1)
                self.section_list = WebDriverWait(self.driver, 10).until(self.find_section_result)
                break
            except TimeoutException as err:
                logging.error("Failed to back to main page: {}".format(err))
                if count > 3:
                    break
                count += 1
                self.set_sleep_scale(2)
            except Exception as err:
                logging.error("Failed to back to main page: {}".format(err))
                if count > 2:
                    break
                count += 1
                self.set_sleep_scale(1)

    def set_sleep_scale(self, sec):
        time.sleep(sleep_scale * sec)

    def get_element_text_by_xpath(self, xpath):
        try:
            elem = self.driver.find_element_by_xpath(xpath)
            if elem:
                if 'img' in xpath:
                    text = elem.get_attribute('src')
                else:
                    text = elem.text
            else:
                text = ''
        except NoSuchElementException as e:
            text = ''
        return text

    def extract_data_from_xpath(self):
        out = {}
        for key, value in xpath_list.items():
            out[key] = self.get_element_text_by_xpath(value)
            if out[key] and out[key].strip() in ['Add website', 'Add phone number']:
                out[key] = ''
        return out

    def crawl(self):
        while self.do_crawl:
            self.section_list = WebDriverWait(self.driver, 10).until(self.find_section_result)
            self.set_sleep_scale(0.5)
            for element in range(len(self.section_list)):
                out = {}
                title = self.driver.find_elements_by_xpath(title_duplicate_xpath)[element].text

                reg_geo_list = re.findall('@(\d+.\d+),(\d+.\d+),', self.driver.current_url)
                if reg_geo_list:
                    reg_geo_list = reg_geo_list[0]
                    reg_geo = "{},{}".format(reg_geo_list[0], reg_geo_list[1])
                    if not self.repo.checkGeoInTownship(reg_geo, self.profileShahrestanID):
                        logging.info(
                            'Crawl stopped due to incorrect geo_point of section list : {geo_point} doesnt blog to '
                            '{profileShahrestanID} '.format(geo_point=reg_geo,
                                                            profileShahrestanID=self.profileShahrestanID))
                        self.do_crawl = False
                        return

                # check exist record
                if self.repo.checkTitleExist(title, self.profileShahrestanID):
                    logging.info('place title exist in db: ' + str(title))
                    continue

                self.section_list[element].click()
                self.set_sleep_scale(2)

                while True:
                    if 'place' in self.driver.current_url:
                        break

                regex = re.findall('(?<=!3d)(\d+.\d+)!4d(\d+.\d+)', self.driver.current_url)
                print(regex)
                if not regex:
                    logging.info('regex error: ' + str(regex))
                    self.back_to_main_page()
                    continue
                regex = regex[0]
                geo_point = "{},{}".format(regex[0], regex[1])
                out["geo_point"] = geo_point

                if self.repo.checkEntityExist(out):
                    logging.info('geo_point {geo_point} exist in db'.format(geo_point=geo_point))
                    self.back_to_main_page()
                    continue

                # township_id = self.repo.getTownship(geo_point)
                township_id = 2624
                if int(township_id) != self.profileShahrestanID:
                    logging.info(
                        'error geo_point {geo_point} doesnt belong to {profileShahrestanID} '.format(
                            geo_point=geo_point,
                            profileShahrestanID=self.profileShahrestanID))
                    status = status_not_related_to_search
                    out['ProfileShahrestanID'] = township_id
                else:
                    status = status_in_queue
                    out['ProfileShahrestanID'] = self.profileShahrestanID
                out.update(self.extract_data_from_xpath())
                res_entity = self.repo.insertEntity(out, self.category, status)
                if res_entity:
                    logging.info('geo_point {geo_point} successfully inserted to db'.format(geo_point=geo_point))
                    print(res_entity)
                else:
                    logging.info('geo_point {geo_point} failed to inserted to db'.format(geo_point=geo_point))

                self.back_to_main_page()
                self.set_sleep_scale(1)
            self.set_sleep_scale(1)
            next_btn = self.driver.find_element_by_xpath(next_button_xpath)
            enabled = next_btn.is_enabled()
            if not enabled:
                self.do_crawl = False
            else:
                next_btn.click()
            while True:
                if self.driver.current_url.split('data=')[1] != '!4m2!2m1!6e5':
                    break
            self.set_sleep_scale(1)

    def __del__(self):
        self.driver.close()
        del self.repo
