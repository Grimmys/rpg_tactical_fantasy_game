class DummyEntities:
    allies = []
    foes = []
    breakables = []
    chests = []
    fountains = []
    buildings = []
    doors = []


class DummyLevel:
    number = 0
    game_phase = type("GP", (), {"name": "INITIALIZATION"})
    is_game_started = False
    turn = 0
    players = []
    escaped_players = []
    entities = DummyEntities()