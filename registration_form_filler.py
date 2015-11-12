lk__author__ = 'punk'
import lxml
from formasaurus import FormExtractor
import requests

class RegistrationFormFiller(object):

    def __init__(self, url):
        #!needs to take in html
        #words/phrases to check against that indicate that a field
        #is a certain type of field, we'll add to this as we add to
        #forms. This should be checked against field names and placeholders
        #

        self.keywords_dic = {
            "email" : ["user[email]", "email"],
            "email_confirmation" : ["user[email_confirmation]"],
            "name" : ["user[name]"],
            "password" : ["user[password]"],
            "password_confirmation" : ["user[password_confirmation]"],
        }

        self.url = url
        self.fe = FormExtractor.load()
        self.form = self._extract_forms_and_types(url)
        self.action = self.form.action
        self.inputs = self._get_inputs()
        self.filled_inputs = None
        self.filled_form = RegistrationForm()

    def _extract_forms_and_types(self, url):

        r = requests.get(url)
        tree = lxml.html.fromstring(r.text)
        form = self.fe.extract_forms(tree)

        return form[0][0]

    def _get_inputs(self):

        input_dics = []
        for child in self.form.xpath("//input"):
            input_dic = {}
            for k,v in child.items():
                input_dic[k] = v
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

        return filled_inputs

if __name__ == "__main__":

    import json
    ff = RegistrationFormFiller("https://auth.getpebble.com/users/sign_up")
    print json.dumps(ff.fill_form())


    #form = extract_forms_and_types("https://auth.getpebble.com/users/sign_up")[0][0]
    #print form.action
    #print get_inputs(form)