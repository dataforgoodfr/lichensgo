from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

def get_address_from_lat_lon(lat, lon, language='fr'):
    try:
        geolocator = Nominatim(user_agent='lichensgo')
        location = geolocator.reverse((lat, lon), exactly_one=True, language=language)

        # Custom address display (to make it shorter than the default one)
        elements = ['amenity', 'road', 'suburb', 'postcode', 'town', 'city', 'state', 'country']
        address = ', '.join([location.raw.get('address').get(e) for e in elements if location.raw.get('address').get(e)])

        return address
    except GeopyError as e:
        print(f"Error: {e}")
        return None