import json


def filter_dataframe(dataframe, column, value, operator="=="):
    """
    Returns a copy of dataframe, but only with rows where the entry under column
    satisfies (entry operator value). For example, if operator is '==', the
    returned Dataframe will include row_i if (dataframe.iloc[row_i][column] ==
    value).

    Currently supports ==, !=, >, >=, <, and <=.
    """
    if operator == "==":
        return dataframe[dataframe[column] == value]
    elif operator == "!=":
        return dataframe[dataframe[column] != value]
    elif operator == ">":
        return dataframe[dataframe[column] > value]
    elif operator == ">=":
        return dataframe[dataframe[column] >= value]
    elif operator == "<":
        return dataframe[dataframe[column] < value]
    elif operator == "<=":
        return dataframe[dataframe[column] <= value]


def load_ndjson(file_path, encoding="utf-8"):
    """
    Returns the contents of a newline delimited json file, with each line as an element in a list.
    """
    with open(file_path, "r", encoding=encoding) as f:
        lines = f.readlines()
    return [json.loads(line.strip()) for line in lines]


def load_jsonl(file_path):
    """
    Returns the contents of a newline delimited json file, with each line as an element in a list.
    """
    load_ndjson(file_path)
