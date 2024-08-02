""" Configuration yaml parser. """

from typing import Optional
import yaml

def load_parameters(path: str = "admin_parameters.yaml") -> Optional[str]:
    """
    Loads parameters from yaml file.
    Param: path: the path to parameters file.
    Returns: the input file's parameters (if file was found).
    """
    try:
        with open(path, 'r', encoding="utf-8") as file:
            parameters = yaml.load(file, Loader=yaml.FullLoader)
        return parameters
    except FileNotFoundError:
        return None
