import pathlib
import os
import json
from typing import Any

DEFAULT_OPTIONS = {
    "language": "en",
    "move_speed": 4,
    "screen_size": 1
}

options_path = pathlib.Path("saves/options.json")

def load_options():
    """
    Load options from options.json file. If the file does not exist, create it with default options.

    Returns:
    Dictionary containing options
    """
    if options_path.is_file():
        with open(options_path, "r", encoding="utf-8") as options_file:
            options_data = json.load(options_file)
            return options_data
    else:
        os.makedirs("saves", exist_ok=True)
        with open(options_path, "w", encoding="utf-8") as options_file:
            json.dump(DEFAULT_OPTIONS, options_file, indent=4)
        return DEFAULT_OPTIONS

options = load_options()   
    
def get_option(option_name: str):
    """
    Get the value of a specific option.

    Arguments:
    option_name -- Name of the option to retrieve

    Returns:
    Value of the specified option
    """
    return options[option_name]

def save_options():
    """
    Save current options to options.json file.
    """
    with open(options_path, "w", encoding="utf-8") as options_file:
        json.dump(options, options_file, indent=4)

def set_option(option_name: str, value: Any, save: bool = True):
    """
    Set the value of a specific option.

    Arguments:
    option_name -- Name of the option to set
    value -- New value for the option
    """
    options[option_name] = value

    if save:
        save_options()
