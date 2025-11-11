

def load_json_data(file_path: str) -> dict:
    """
    Load JSON data from the given file path.

    Keyword arguments:
    file_path -- the relative path to the JSON file

    Return the loaded JSON data as a dictionary.
    """
    import json


    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    return data


def load_alteration_data() -> dict[str, dict]:
    """
    Load alteration data from JSON files.

    Return a dictionary mapping alteration names to their data.
    """
    return load_json_data("data/alterations.json")