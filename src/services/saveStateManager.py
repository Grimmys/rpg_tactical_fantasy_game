from lxml import etree


class SaveStateManager:
    def __init__(self, data):
        self.level = data
        # Init XML tree
        self.tree = etree.Element('save')

    def save_game(self, file_id):
        save_file = open(f"saves/save_{file_id}.xml", "w+")

        level = self.save_level()
        self.tree.append(level)

        # Store XML tree in file
        save_file.write(etree.tostring(self.tree, pretty_print=True, encoding="unicode"))

        save_file.close()

    def save_level(self):
        level = etree.Element('level')

        # Save level identity
        index = etree.SubElement(level, 'index')
        index.text = str(self.level.nb_level)

        # Save game phase
        phase = etree.SubElement(level, 'phase')
        phase.text = self.level.game_phase.name

        # Save turn if game has started
        if self.level.is_game_started:
            turn = etree.SubElement(level, 'turn')
            turn.text = str(self.level.turn)

        # Save current entities stats and position
        entities = self.save_entities()
        level.append(entities)

        return level

    def save_entities(self):
        entities = etree.Element('entities')

        entities.append(self.save_collection('allies', 'ally', self.level.entities['allies']))
        entities.append(self.save_collection('foes', 'foe', self.level.entities['foes']))
        entities.append(self.save_collection('breakables', 'breakable', self.level.entities['breakables']))
        entities.append(self.save_collection('chests', 'chest', self.level.entities['chests']))
        entities.append(self.save_collection('fountains', 'fountain', self.level.entities['fountains']))
        entities.append(self.save_collection('buildings', 'building', self.level.entities['buildings']))
        entities.append(self.save_collection('doors', 'door', self.level.entities['doors']))
        entities.append(self.save_collection('players', 'player', self.level.players))
        entities.append(self.save_collection('escaped_players', 'player', self.level.passed_players))

        return entities

    @staticmethod
    def save_collection(collection_name, element_name, collection):
        element = etree.Element(collection_name)
        element.extend([ent.save(element_name) for ent in collection])
        return element
