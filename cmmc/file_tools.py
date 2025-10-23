import json
from pathlib import Path


def load_ndjson(file_path: str | Path, encoding: str = "utf-8"):
    """
    Returns the contents of a newline delimited json file, with each line as an element in a list.
    """
    with open(file_path, "r", encoding=encoding) as f:
        lines = f.readlines()
    return [json.loads(line.strip()) for line in lines]


def load_jsonl(file_path: str | Path, encoding: str = "utf-8"):
    """
    Returns the contents of a newline delimited json file, with each line as an element in a list.
    """
    load_ndjson(file_path, encoding)
