from selenium import webdriver
from registration_form_filler import RegistrationFormFiller


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

    def crawl(self, url):
        print('Requesting {}'.format(url))
        self.browser.get(url)
        html = self.browser.page_source
        form_filler = RegistrationFormFiller(html)
        form_data = form_filler.fill_form()
        self.submit_reg_form(form_data)

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
    print 'start'
    main()
