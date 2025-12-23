# Autoregister

Automatically detect and fill registration forms for testing purposes.

## Overview

Autoregister is a Python library that helps automate the process of filling out registration forms on websites. It uses machine learning (via formasaurus) to detect form fields and intelligently fills them with appropriate test data.

## Features

- **Automatic Field Detection**: Uses formasaurus to extract and classify form fields
- **Smart Field Filling**: Detects field types (email, password, name, etc.) and fills with appropriate values
- **Multiple Usage Modes**:
  - Get filled form data for use with Selenium/browser automation
  - Get form data as POST dictionary for HTTP requests
  - Automatically submit forms via HTTP POST
- **Flexible Input**: Works with either HTML content or URLs

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Form Filling

```python
from registration_form_filler import RegistrationFormFiller

# Create a filler from a URL
filler = RegistrationFormFiller(url='https://example.com/register')

# Fill the form
form_data = filler.fill_form()
print(form_data)
```

### Use with Selenium

```python
from selenium import webdriver
from registration_form_filler import RegistrationFormFiller

# Get the page
browser = webdriver.Firefox()
browser.get('https://example.com/register')
html = browser.page_source

# Fill the form
filler = RegistrationFormFiller(html_in=html)
form_data = filler.fill_form()

# Submit using Selenium
for field in form_data:
    if 'value' in field and 'xpath' in field:
        element = browser.find_element_by_xpath(field['xpath'])
        element.send_keys(field['value'])
```

### Submit via HTTP POST

```python
from registration_form_filler import RegistrationFormFiller

# Create and fill the form
filler = RegistrationFormFiller(url='https://example.com/register')
filler.fill_form()

# Get as POST data
post_data = filler.get_form_as_post_data()
print(post_data)  # {'email': 'test@example.com', 'password': 'secret123', ...}

# Or submit directly
response = filler.submit_form(base_url='https://example.com')
print(response.status_code)
```

### Use with HTML Content

```python
from registration_form_filler import RegistrationFormFiller

html = '''
<form action="/register" method="post">
    <input name="email" type="email" />
    <input name="password" type="password" />
    <input type="submit" value="Register" />
</form>
'''

filler = RegistrationFormFiller(html_in=html)
form_data = filler.fill_form()
```

## Demo Spiders

The repository includes two demo spiders that show complete registration workflows:

- `demo_spider_1.py`: Basic registration automation with Selenium
- `demo_spider_2.py`: Advanced registration with CAPTCHA solving and email verification

## API Reference

### RegistrationFormFiller

Main class for filling registration forms.

#### Methods

- `__init__(html_in=None, url=None)`: Initialize with HTML content or URL
- `fill_form()`: Detect and fill form fields, returns list of field data
- `get_form_as_post_data()`: Get filled form as dictionary for POST requests
- `submit_form(base_url=None)`: Submit the form via HTTP POST
- `prepare_registration_form()`: Prepare form data in RegistrationForm object

### RegistrationForm

Class representing a filled registration form.

#### Methods

- `__init__(**kwargs)`: Initialize empty form
- `add_attribute(name, value)`: Add a field to the form
- `get_as_raw_post()`: Get form data as dictionary for POST requests

## Field Type Detection

The library automatically detects the following field types:

- Email fields
- Email confirmation fields
- Password fields
- Password confirmation fields
- Name fields

Detection is based on field names and placeholder text using a keyword dictionary that can be customized.

## Default Values

The library uses the following default values for testing:

- Email: `blabhalbhalbhalbahlbah@blah.com`
- Password: `r@nd0mP@ssw0rd`
- Name: `Random Name`

## Requirements

- Python 2.7+ (original code) or Python 3.x
- formasaurus
- lxml
- requests
- selenium (for demo spiders)
- Additional dependencies for advanced features (see requirements.txt)

## Contributing

This is a research/testing tool. Contributions are welcome!

## License

See repository for license information.

## Disclaimer

This tool is for testing and research purposes only. Always ensure you have permission before automating registration on any website.
