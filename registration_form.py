class RegistrationForm(object):
    """
    Represents a registration form with fields and values.
    
    This class stores form field data and provides methods to retrieve
    the data in formats suitable for form submission.
    
    Attributes:
        attribute_dict (dict): Dictionary storing field names and their values
    
    Example:
        >>> form = RegistrationForm()
        >>> form.add_attribute('email', 'test@example.com')
        >>> form.add_attribute('password', 'secret123')
        >>> form.get_as_raw_post()
        {'email': 'test@example.com', 'password': 'secret123'}
    """

    def __init__(self, **kwargs):
        self.attribute_dict = {}

    def add_attribute(self, name, value):
        """
        Add a form field and its value.
        
        Args:
            name (str): The field name (e.g., 'email', 'password')
            value (str): The field value
        """
        self.attribute_dict[name] = value

    def get_as_raw_post(self):
        """
        Return the form data as a dictionary suitable for POST requests.
        
        Returns:
            dict: Dictionary mapping field names to their values, ready
                  to be used with requests.post(data=...)
        """
        return self.attribute_dict