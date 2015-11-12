import base64
from StringIO import StringIO
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import deathbycaptcha as dbc
import time


class Spider():
    max_api_requests = 4
    wait_time = 30
    max_solve_attempts = 5
    max_parse_attempts = 3
    max_http_retries = 2

    def __init__(self):
        print 'Starting browser'
        self.browser = webdriver.Firefox()
        self.browser.set_page_load_timeout(5)
        self.dbc_client = dbc.SocketClient('hyperion_blue', 'b0000000000')
        self.form_data = [
            {
                'type': 'text',
                'xpath': "//form//input[@name='userName']",
                'value': 'ba'
            },
            {
                'type': 'password',
                'xpath': "//form//input[@name='userPassword']",
                'value': 'ba'
            },
            {
                'type': 'text',
                'xpath': "//form//input[@name='userEmail']",
                'value': 'ba'
            },
            {
                'type': 'text',
                'xpath': "//form//input[@name='userEmailConfirm']",
                'value': 'ba'
            },
            {
                'type': 'text',
                'xpath': "//form//input[@name='userNameReal']",
                'value': 'ba'
            },
            {
                'type': '',
                'xpath': "//form//select[@name='state']",
                'value': 'ba'
            },
            {
                'type': '',
                'xpath': "//form//select[@name='country']",
                'value': 'ba'
            },
            {
                'type': '',
                'xpath': "//form//select[@name='userPrefNewThreadView']",
                'value': 'ba'
            },
            {
                'type': '',
                'xpath': "//form//select[@name='userTimezoneID']",
                'value': 'ba'
            },
            {
                'type': 'checkbox',
                'xpath': "//form//input[@name='userNewsletter']",
                'value': 1
            },
            {
                'type': 'checkbox',
                'xpath': "//form//input[@name='userAgreement']",
                'value': 1
            },
            {
                'type': 'text',
                'xpath': "//form//input[@name='imagecheck']",
                'value': ''
            },
            {
                'type': 'submit',
                'xpath': "//form//img[contains(@src, 'captcha')]",
                'value': ''
            },
        ]

    def get_captcha_element(self):
        xpaths = [
            '//form//img[contains(@src, "captcha")]'
        ]
        for xpath in xpaths:
            try:
                element = self.browser.find_element_by_xpath(xpath)
                return element
            except NoSuchElementException:
                pass
        return None

    def get_captcha_image(self, location, size):
        screenshot = self.browser.get_screenshot_as_base64()
        im = Image.open(StringIO(base64.decodestring(screenshot)))
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        captcha_image = im.crop((left, top, right, bottom))
        captcha_image.save('captcha.png')

    def add_captcha_solution(self, solution):
        for row in self.form_data:
            if 'imagecheck' in row['xpath']:
                row['value'] = solution


    def crawl(self, url):
        print('Requesting {}'.format(url))
        self.browser.get(url)
        print('done')
        logged_in = False
        while not logged_in:
            captcha_element = self.get_captcha_element()
            if captcha_element is not None:
                location = captcha_element.location
                size = captcha_element.size
                self.get_captcha_image(location, size)
                solution = self.get_captcha_solution('captcha.png')
                print(solution)
                self.add_captcha_solution(solution)
                self.submit_reg_form(self.form_data)
                logged_in = True

    def get_captcha_solution(self, filename):
        print 'Requesting solution...'
        done = False
        success = False
        attempts = 0
        solution = None
        while not done:
            attempts += 1
            if attempts > self.max_api_requests:
                print 'Max API attempts reached. Exiting'
                done = True
            try:
                solution = self.dbc_client.decode(filename, 20)
                print 'Solution obtained'
                if solution is not None and len(solution) > 0:
                    done = True
                else:
                    solution = None
                    print('API request {} failed. Solution was empty. '
                          'Waiting {} then trying again..'
                          .format(attempts, self.wait_time)
                          )
            except Exception as e:
                print e
                time.sleep(self.wait_time)
                pass
        return solution

    def submit_reg_form(self, form_data):
        for row in form_data:
            if row['type'] == 'submit':
                submit_xpath = row['xpath']
            else:
                if row['type'] == 'select':
                    xpath = row['xpath'] +  "/option[text()='{}']".format(row['value'])
                    self.browser.find_element_by_xpath(xpath).click()
                elif row['type'] == 'checkbox':
                    self.browser.find_element_by_xpath(row['xpath']).click()
                else:
                    element = self.browser.find_element_by_xpath(row['xpath'])
                    element.send_keys(row['value'])
        self.browser.find_element_by_xpath(submit_xpath).click()

def main():
    url = 'https://www.ar15.com/member/register.html'
    spider = Spider()
    html = spider.crawl(url)

if __name__ == '__main__':
    print 'start'
    main()


