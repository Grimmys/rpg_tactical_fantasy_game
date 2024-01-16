from collections.abc import Sequence

from lxml import etree
from lxml.etree import Element

from src.game_entities.entity import Entity


class SaveStateManager:
    """ """

    def __init__(self, data):
        self.level = data
        # Init XML tree
        self.tree = etree.Element("save")

    def save_game(self, file_id):
        """
        Save the current state of the game to the given file in XML format

        Keyword Arguments:
        file_id -- the id of the save file to use
        """
        with open(f"saves/save_{file_id}.xml", "w+", encoding="utf-8") as save_file:
            level = self._save_level()
            self.tree.append(level)

            # Store XML tree in file
            save_file.write(
                etree.tostring(self.tree, pretty_print=True, encoding="unicode")
            )

    def _save_level(self):
        """

        :return:
        """
        level = etree.Element("level")

        # Save level identity
        index = etree.SubElement(level, "index")
        index.text = str(self.level.number)

        # Save game phase
        phase = etree.SubElement(level, "phase")
        phase.text = self.level.game_phase.name

        # Save turn if game has started
        if self.level.is_game_started:
            turn = etree.SubElement(level, "turn")
            turn.text = str(self.level.turn)

        # Save current entities stats and position
        entities = self._save_entities()
        level.append(entities)

        return level

    def _save_entities(self):
        """

        :return:
        """
        entities = etree.Element("entities")
        entities.extend(
            [
                self.save_collection("allies", "ally", self.level.entities.allies),
                self.save_collection("foes", "foe", self.level.entities.foes),
                self.save_collection(
                    "breakables", "breakable", self.level.entities.breakables
                ),
                self.save_collection("chests", "chest", self.level.entities.chests),
                self.save_collection(
                    "fountains", "fountain", self.level.entities.fountains
                ),
                self.save_collection(
                    "buildings", "building", self.level.entities.buildings
                ),
                self.save_collection("doors", "door", self.level.entities.doors),
                self.save_collection("players", "player", self.level.players),
                self.save_collection(
                    "escaped_players", "player", self.level.escaped_players
                ),
            ]
        )
        return entities

    @staticmethod
    def save_collection(
        collection_name: str, element_name: str, collection: Sequence[Entity]
    ) -> Element:
        """

        :param collection_name:
        :param element_name:
        :param collection:
        :return:
        """
        element = etree.Element(collection_name)
        element.extend([entity.save(element_name) for entity in collection])
        return element
