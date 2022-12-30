from geograpy import extraction
import numpy as np

def get_location_from_text(text):
    """
    text: input text to extract geography from.
    """
    place_list = extraction.Extractor(text=text)
    entities = place_list.find_entities()

    if not entities:
        return np.nan
    else:
        return entities


def get_lat_lon(location_name: str, key_file_path: str):
    """
    Use arcgis geocoder to return lat and longitude from text input
    """
    import geocoder
    g = geocoder.arcgis(location_name, key=key_file_path)
    return g.latlng

