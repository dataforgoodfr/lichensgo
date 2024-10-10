import os
import cssutils

# Get the absolute path to the CSS file in the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
css_file_path = os.path.join(parent_dir, 'assets', 'styles.css')

# Load the CSS file
with open(css_file_path, "r") as file:
    css_content = file.read()

# Parse the CSS
css_parser = cssutils.parseString(css_content)

def get_css_properties(selector):
    properties = {}
    for rule in css_parser:
        if rule.type == rule.STYLE_RULE and rule.selectorText == selector:
            for property in rule.style:
                properties[property.name] = property.value
                # if property.value:  # Check if the property has a non-empty value

    return properties
