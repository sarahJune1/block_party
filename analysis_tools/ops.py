
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