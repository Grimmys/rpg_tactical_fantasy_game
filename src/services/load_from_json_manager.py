import json

from .load_from_xml_manager import get_skill_data

RACES_DATA_PATH = "data/races.json"


def load_races() -> dict[str, dict[str, any]]:
    with open(RACES_DATA_PATH, "r", encoding="utf-8") as file:
        races = json.load(file)
    for race in races.values():
        race["constitution"] = race.get("constitution", 0)
        race["move"] = race.get("move", 0)
        race["skills"] = [
            get_skill_data(skill) for skill in race.get("skills", [])
        ]
    return races
