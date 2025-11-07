import json
from pathlib import Path
from typing import List


def discover_files_with_name(name: str, dir: Path) -> List[Path]:
    """
    Recursively find all files with the same name (ex. "foo.bar") under the
    given directory.
    """
    if not isinstance(name, str):
        raise ValueError(f"Expecting string but received {type(name)}: {name}")

    if not isinstance(dir, Path):
        raise ValueError(f"Expecting Path but received {type(dir)}: {dir}")

    return list(dir.rglob(name))


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
