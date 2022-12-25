import pandas as pd

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
    print('Dataframe created...')
    cols_to_drop = []
    for i in columns_to_output:
        _key, _value = i.split('.')
        # drop the parent column after unnesting
        if _key not in cols_to_drop:
            cols_to_drop.append(_key)
        try:
            df[_value] = df[_key].transform(lambda x: x[_value])
            print(f'Transformed col {_value}...')
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

    def filter_by_regex(self, field, regex_list: list, projection=None):
        """Filter the collection by a field matching a regular expression.
        
        Args:
            field (str): The field to filter by.
            regex_list (list): The regular expression to match.
        
        Returns:
            A cursor containing the matching documents.
        """
        # convert list into single regex pattern
        regex = "|".join(regex_list)
        print("searching for:", regex)
        query = {field: {'$regex': regex}}

        return self.collection.find(query, projection=projection)









    