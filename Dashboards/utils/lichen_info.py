import re
import requests

def remove_special_characters(name):
    """
    Remove all special characters from the given string.

    Parameters:
    - name (str): The string to clean.

    Returns:
    - str: The cleaned string with all special characters removed.
    """
    return re.sub(r'[^A-Za-z0-9\s]', '', name)


def fetch_image(lichen_name):

    lichen_name = remove_special_characters(lichen_name)
    # Query the Wikimedia API for images related to the lichen name
    search_url = "https://commons.wikimedia.org/w/api.php"

    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': lichen_name,
        'srlimit': 1,  # Limit to one result
        'prop': 'imageinfo',
        'iilimit': 1,
        # 'iiurlwidth': 800,  # Width of the image to retrieve
        # 'iiurl': True
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    print(lichen_name)

    print(data)

    # Check if any results were found
    if 'query' in data and 'search' in data['query']:
        page_title = data['query']['search'][0]['title']
        image_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{page_title.replace(' ', '_')}.jpg"
        return image_url

    return "https://wiki.tripwireinteractive.com/TWIimages/4/47/Placeholder.png?20121020050736"

if __name__ == "__main__":
    lichen_name = "Cladonia rangiferina"
    lichen_name = "anaptychia ciliaris"
    image_url = fetch_image(lichen_name)
    print(f"Image URL for '{lichen_name}': {image_url}")
