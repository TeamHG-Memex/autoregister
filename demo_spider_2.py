import base64
from StringIO import StringIO
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import deathbycaptcha as dbc
import time
import string
import tldextract
from random import *
from formail import Formail
from faker import Faker


class Spider():
    max_api_requests = 4
    wait_time = 30
    max_solve_attempts = 5
    max_parse_attempts = 3
    max_http_retries = 2
    user = None
    email = None

    def __init__(self):
        print 'Starting browser'
        self.browser = webdriver.Firefox()
        self.browser.set_page_load_timeout(5)
        self.browser.set_window_size(960, 1080)
        self.browser.set_window_position(960, 0)
        self.dbc_client = dbc.SocketClient('hyperion_blue', 'b0000000000')
        self.formail = Formail()
        self.faker = Faker()

    def generate_password(self):
        characters = string.ascii_letters + string.punctuation  + string.digits
        password =  "".join(choice(characters) for x in range(8))
        return password

    def get_form_data(self):
        email = self.formail.get_email_address()
        tokens = email.split('@')
        self.user = tokens[0]
        self.email = self.user + '@grr.la'
        profile = self.faker.profile(fields=None)
        form_data = [
            {
                'type': 'text',
                'xpath': "//form//input[@name='userName']",
                'value': profile['username'].replace('.', '')
            },
            {
                'type': 'password',
                'xpath': "//form//input[@name='userPassword']",
                'value': 'b000000000'
            },
            {
                'type': 'text',
                'xpath': "//form//input[@name='userEmail']",
                'value': self.email
            },
            {
                'type': 'text',
                'xpath': "//form//input[@name='userEmailConfirm']",
                'value': self.email
            },
            {
                'type': 'text',
                'xpath': "//form//input[@name='userNameReal']",
                'value': profile['name']
            },
            {
                'type': '',
                'xpath': "//form//select[@name='state']",
                'value': 'AK'
            },
            {
                'type': '',
                'xpath': "//form//select[@name='country']",
                'value': 'USA'
            },
            {
                'type': '',
                'xpath': "//form//select[@name='userPrefNewThreadView']",
                'value': '1'
            },
            {
                'type': '',
                'xpath': "//form//select[@name='userTimezoneID']",
                'value': '1'
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
                'type': 'submit',
                'xpath': "//form//img[contains(@src, 'Submit')]",
                'value': ''
            },
        ]
        return form_data

    def get_domain(self, url):
        ext = tldextract.extract(url)
        return '.'.join([ext.domain, ext.suffix])

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

    def crawl(self, url):
        print('Requesting {}'.format(url))
        self.browser.get(url)
        logged_in = False
        while not logged_in:
            captcha_element = self.get_captcha_element()
            if captcha_element is not None:
                print 'Detected captcha'
                print 'Taking screenshot of captcha image'
                location = captcha_element.location
                size = captcha_element.size
                self.get_captcha_image(location, size)
                print 'Solving captcha...'
                solution = self.get_captcha_solution('captcha.png')
                print(solution)
                form_data = self.get_form_data()
                form_data.append(
                    {
                        'type': 'text',
                        'xpath': "//form//input[@name='imagecheck']",
                        'value': solution['text']
                    }
                )
                self.submit_reg_form(form_data)
                domain = self.get_domain(url)
                verify_link = None
                time.sleep(5)
                while verify_link is None:
                    verify_link = self.get_verify_link(domain)
                    time.sleep(5)
                self.browser.get(verify_link)

    def get_verify_link(self, domain):
        self.formail.set_email_address(self.user)
        email = self.formail.fetch_verfiy_email(domain)
        if email is not None:
            link = self.formail.extract_verfiy_link(email, domain)
            print(link)
            return link
        else:
            print('No email')
            return None



    def get_captcha_solution(self, filename):
        print 'Requesting solution...'
        done = False
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
                    xpath = row['xpath'] + "/option[text()='{}']"\
                        .format(row['value'])
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
    spider.crawl(url)

if __name__ == '__main__':
    main()
