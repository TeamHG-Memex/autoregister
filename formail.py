import requests
import re
from lxml import html
from lxml.etree import HTMLParser


class Formail():
    '''
    Class for interacting with guerrilamail API and parsing verification links
    from account verification emails
    '''

    def __init__(self):
        self.client_ip = '127.0.0.1'
        self.api_url = 'http://api.guerrillamail.com/ajax.php'
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) '\
                          'Gecko/20100101 Firefox/40.1'
        self.parser = HTMLParser(recover=True, encoding='utf-8')
        self.verify_keywords = [
            'verify',
            'verifyemail',
            'verification',
            'confirm',
        ]
        self.session = requests.session()

    def default_kwargs(self):
        '''
        Default API parameters required for every request.
        '''
        kwargs = {
            'ip': self.client_ip,
            'agent': self.user_agent,
        }
        return kwargs

    def get_email_address(self):
        '''
        Get a random email address from guerillamail.
        '''
        kwargs = self.default_kwargs()
        f = 'get_email_address'
        kwargs['f'] = f
        response = self.session.get(self.api_url, params=kwargs)
        return response.json()['email_address']

    # Set an email address
    def set_email_address(self, user):
        kwargs = self.default_kwargs()
        f = 'set_email_user'
        kwargs['f'] = f
        kwargs['email_user'] = user
        kwargs['lang'] = 'en'
        response = self.session.get(self.api_url, params=kwargs)
        if response.status_code != 200:
            raise
        json_data = response.json()
        return json_data

    # Check emails
    def fetch_emails(self):
        kwargs = self.default_kwargs()
        f = 'check_email'
        seq = 1
        kwargs['f'] = f
        kwargs['seq'] = seq
        response = self.session.get(self.api_url, params=kwargs)
        if response.status_code != 200:
            raise
        return response.json()['list']

    def fetch_email(self, email_id):
        kwargs = self.default_kwargs()
        f = 'fetch_email'
        kwargs['f'] = f
        kwargs['email_id'] = email_id
        response = self.session.get(self.api_url, params=kwargs)
        if response.status_code != 200:
            raise
        return response.json()

    def fetch_verfiy_email(self, domain):
        emails = self.fetch_emails()
        verfiy_email = None
        for email in emails:
            if domain in email['mail_from']:
                email_id = email['mail_id']
                verfiy_email = self.fetch_email(email_id)
        return verfiy_email

    def extract_verfiy_link(self, email, domain):
        """

        """
        html_body = email['mail_body']
        links = self.extract_links(html_body)
        for link in links:
            if self.is_verify_link(link):
                return link

    def extract_tokens(self, text):
        """
        Tokenize a string, replacing nonalphanumeric characters.
        Used to match against verify keywords.
        """
        # Split by non-alphanumeric characters
        keyword_list = re.findall(r'\w+', text)
        # Create sanitized list,
        # ignoring digits and any remaining irrelevant characters
        sanitized_list = []

        for keyword in keyword_list:
            if not keyword.isdigit():
                keyword = keyword.replace('_', ' ')
                keyword = keyword.replace('-', ' ')
                keyword = keyword.strip()
                sanitized_list.append(keyword.lower())

        return sanitized_list

    def extract_links(self, html_source):
        """
        Extract login links from html source.
        """
        results = []
        doc = html.document_fromstring(html_source, self.parser)
        links = doc.xpath('//a')

        for link in links:
            # Ignore links without href
            try:
                href = link.xpath('@href')[0]
            except:
                continue

            results.append(href)

        return results

    def is_verify_link(self, url):
        """
        Take an lxml link element and test whether it is a verfification link.
        """
        # Tokenize href
        url_tokens = self.extract_tokens(url)
        matches = set(url_tokens) & set(self.verify_keywords)

        if len(matches) > 0:
                return True
        return False


if __name__ == '__main__':
    # Example usage
    user = 'uflkhlzg'
    formail = Formail()
    formail.set_email_address(user)
    domain = 'ar15.com'
    email = formail.fetch_verfiy_email(domain)
    if email is not None:
        link = formail.extract_verfiy_link(email, domain)
        print link
    else:
        print('No email')
