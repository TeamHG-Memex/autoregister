class RegistrationForm(object):

    def __init__(self, **kwargs):
        self.attribute_dict = {}

    def add_attribute(self, name, value):
        self.attribute_dict[name] = value

    def get_as_raw_post(self):
        pass