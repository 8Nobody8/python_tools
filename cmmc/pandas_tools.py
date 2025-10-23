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
