from src.game_entities.foe import Foe

foes_by_mission: dict[str, list[Foe]] = {}

def link_foe_to_mission(foe: Foe, mission_id: str) -> None:
    if mission_id not in foes_by_mission:
        foes_by_mission[mission_id] = []
    foes_by_mission[mission_id].append(foe)

