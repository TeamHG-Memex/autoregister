import re

class DumbHeuristics(object):

    def __init__(self):


    def _simple_tokenize(self, _string):
        return re.sub('[^0-9a-zA-Z]+', ' ', _string)

    def field_fill(self, name, default_value = None):

        if "email" in name:
            tokenize = self._simple_tokenize(name)



if __name__ == "__main__":
    dh = DumbHeuristics()
    print dh.email_field_fill("email[password]")
