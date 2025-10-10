__author__ = 'punk'
import lxml
from lxml import etree
from formasaurus import FormExtractor
import requests
from registration_form import RegistrationForm

class RegistrationFormFiller(object):

    def __init__(self, html_in = None, url = None):
        #!needs to take in html
        #words/phrases to check against that indicate that a field
        #is a certain type of field, we'll add to this as we add to
        #forms. This should be checked against field names and placeholders

        self.keywords_dic = {
            "email" : ["user[email]", "email"],
            "email_confirmation" : ["user[email_confirmation]"],
            "name" : ["user[name]"],
            "password" : ["user[password]"],
            "password_confirmation" : ["user[password_confirmation]"],
        }

        self.html_in = html_in

        if not self.html_in:
            r = requests.get(url)
            self.html_in = r.text

        print self.html_in

        self.fe = FormExtractor.load()
        self.form = self._extract_forms_and_types(self.html_in)
        self.action = self.form.action
        self.inputs = self._get_inputs()
        self.filled_inputs = None
        self.filled_form = RegistrationForm()

    def _extract_forms_and_types(self, html_in):

        self.tree = lxml.html.fromstring(html_in)
        form = self.fe.extract_forms(self.tree)

        return form[0][0]

    def _get_inputs(self):

        input_dics = []
        self.some_tree = self.tree.getroottree()
        for child in self.form.xpath("//input"):
            input_dic = {}
            for k,v in child.items():
                input_dic[k] = v
            #get xpath
            input_xpath = self.some_tree.getpath(child)
            input_dic["xpath"] = input_xpath
            input_dics.append(input_dic)

        return input_dics

    def _normalize_field_value(self, value):

        if value.strip() == "":
            return None

        if value.strip():
            return value.strip()

    def _detect_input_types(self):

        forms_with_type = []
        for input in self.inputs:
            filled_input_and_type = {}
            if "name" in input:
                detected_type = self._find_in_keywords_dic(input["name"])
                input["detected_type"] = detected_type
                forms_with_type.append(input)

        #will produce duplicates
        for input in self.inputs:
            filled_input_and_type = {}
            if "detected_type" not in input and "placeholder" in input:
                detected_type = self._find_in_keywords_dic(input["placeholder"])
                input["detected_type"] = detected_type
                forms_with_type.append(input)

        self.forms_with_type = forms_with_type
        print self.forms_with_type

        return forms_with_type

    def _find_in_keywords_dic(self, name_or_placeholder):

        #search through the keywords_dic for name_or_placeholder
        #in the keywords_dic, if it's found in one of the lists
        #of words return the list it was found in (email, email
        # confirmation, etc)
        for k,v in self.keywords_dic.iteritems():
            if name_or_placeholder in v:
                return k
        return None

    def prepare_registration_form(self):

        for input in self.inputs:
            field_name = input["name"]
            if "value" in input:
                field_value = input["value"]
            else:
                field_value = None

            self.filled_form.add_attribute(field_name, field_value)

        return self.filled_form.attribute_dict

    def fill_form(self):

        self._detect_input_types()

        filled_inputs = []
        for input in self.forms_with_type:
            if "detected_type" in input:
                if input["detected_type"] == "email":
                    input["value"] = "blabhalbhalbhalbahlbah@blah.com"
                if input["detected_type"] == "email_confirmation":
                    input["value"] = "blabhalbhalbhalbahlbah@blah.com"
                if input["detected_type"] == "name":
                    input["value"] = "Random Name"
                if input["detected_type"] == "password":
                    input["value"] = "r@nd0mP@ssw0rd"
                if input["detected_type"] == "password_confirmation":
                    input["value"] = "r@nd0mP@ssw0rd"

            filled_inputs.append(input)
            
            # Populate the RegistrationForm object
            if "name" in input and "value" in input:
                self.filled_form.add_attribute(input["name"], input["value"])

        return filled_inputs
    
    def get_form_as_post_data(self):
        """
        Get the filled form data as a dictionary suitable for POST requests.
        Calls fill_form() if not already called, then returns the POST data.
        """
        if not self.filled_inputs:
            self.filled_inputs = self.fill_form()
        return self.filled_form.get_as_raw_post()
    
    def submit_form(self, base_url=None):
        """
        Submit the filled form via HTTP POST.
        
        Args:
            base_url: Base URL to use if form action is relative. If None, 
                     uses the URL passed to __init__.
        
        Returns:
            requests.Response object
        """
        if not self.filled_inputs:
            self.filled_inputs = self.fill_form()
        
        post_data = self.get_form_as_post_data()
        
        # Determine the submission URL
        action = self.action
        if action.startswith('http'):
            submit_url = action
        elif action.startswith('/'):
            # Absolute path - need base URL
            if not base_url:
                raise ValueError("Form action is absolute path but no base_url provided")
            submit_url = base_url.rstrip('/') + action
        else:
            # Relative path
            if not base_url:
                raise ValueError("Form action is relative but no base_url provided")
            submit_url = base_url.rstrip('/') + '/' + action
        
        # Submit the form
        response = requests.post(submit_url, data=post_data)
        return response

if __name__ == "__main__":

    import json
    ff = RegistrationFormFiller(url = "https://auth.getpebble.com/users/sign_up")
    print json.dumps(ff.fill_form())


    #form = extract_forms_and_types("https://auth.getpebble.com/users/sign_up")[0][0]
    #print form.action
    #print get_inputs(form)