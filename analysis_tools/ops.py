
import yaml
import pandas as pd

class Constants:
    """
    Reads in yaml file as constants
    """
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.constants = yaml.safe_load(f)


def pass_key(key_path: str):
        """Access API key and return as client address.

            Returns:
                String with the API key saved to .txt file
        """
        import os
        path = f'{key_path}'
        os.environ['PATH'] += ':'+path
        with open(f"{path}.txt", "r") as f:
            data = f.readlines()

        client_address = data
        return client_address


def counter_dict(input_list):
    """
    Input list is made into counter dictionary object

        Returns:
            counter object
    """
    import itertools
    from collections import Counter
    counter_object = Counter(list(itertools.chain.from_iterable(input_list)))
    return counter_object


def analyze_by_cb(cb_name, col_extract, df, list_to_remove):
    subset = df[(df['normalizedName'] == cb_name)]
    subset_top = counter_dict(subset[subset[col_extract].notna()][col_extract])

    for i in range(len(list_to_remove)):
    #print(not_areas[i])
        if list_to_remove[i] in subset_top:
            print("Removing...")
            print(list_to_remove[i])
            del(subset_top[list_to_remove[i]])

    return subset_top