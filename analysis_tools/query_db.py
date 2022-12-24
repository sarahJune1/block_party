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


def flatten_docs_by_columns(results: object, columns_to_output: list):
    """
    Flatten object of docs from mongodb using columns specified
    
    Args:
        results: mongodb object
        columns_to_output: list of columns with nested properties from document dictionary
    
    Returns: 
        df: Filtered dataframe with only desired columns remaining

    """
    import numpy as np
    print('Creating dataframe from database query...')
    df = pd.DataFrame(results)
    cols_to_drop = []
    for i in columns_to_output:
        _key, _value = i.split('.')
        # drop the parent column after unnesting
        if _key not in cols_to_drop:
            cols_to_drop.append(_key)
        try:
            df[_value] = df[_key].transform(lambda x: x[_value])
        except ValueError as e:
            print('value: ', _value, 'not found')
    
    # drop the redundant columns that are unpacked
    df.drop(columns=cols_to_drop, inplace=True)

    return df


class MongoDBFilter:
    """
    Filter mongodb object class
    """
    def __init__(self, client, db_name: str, collection_name: str):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    def filter_by_regex(self, field, regex, projection=None):
        """Filter the collection by a field matching a regular expression.
        
        Args:
            field (str): The field to filter by.
            regex (str): The regular expression to match.
        
        Returns:
            A cursor containing the matching documents.
        """
        print("searching for:", regex)
        query = {field: {'$regex': regex}}

        return self.collection.find(query, projection=projection)









    