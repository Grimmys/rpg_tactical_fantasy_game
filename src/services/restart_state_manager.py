from collections.abc import Sequence

from lxml import etree
from lxml.etree import Element

from src.game_entities.entity import Entity
from src.services import load_from_xml_manager as xml_loader
from typing import Optional 


class RestartStateManager:
    """ """

    def __init__(self, data):
        self.level = data
        # Init XML tree
        self.tree = etree.Element("save")
        self.entities_data: Optional[etree.Element] = None

    def restart_game(self, file_id):
        """
        Restart_game
        """
        with open(f"saves/save_{file_id}.xml", "r", encoding="utf-8") as save_file:
            tree_root: etree.Element = etree.parse(save_file).getroot()
            level_id = int(tree_root.find("level/index").text.strip())
            level_path = f"maps/level_{level_id}/"
            game_status = tree_root.find("level/phase").text.strip()
            turn_nb = int(tree_root.find("level/turn").text.strip())

            level = self._save_level(tree_root, level_id, game_status,turn_nb)
            self.tree.append(level)

            # save_file.write(
            #     etree.tostring(self.tree, pretty_print=True, encoding="unicode")
            # )


    def _save_level(self,tree_root, level_id, game_status,turn_nb):

        level = etree.Element("level")

        print("------------------------------------")
        # Save level identity
        index = etree.SubElement(level, "index")
        index.text = str(self.level.number)
        print("self.level.number:",self.level.number)
        self.level.number = level_id
        # self.level.number = 0

        # Save game phase
        phase = etree.SubElement(level, "phase")
        phase.text = self.level.game_phase.name
        # print("self.game_phase (before):",self.level.game_phase.name)
        # self.level.game_phase.name = game_status
        # print("self.game_phase (after):",self.level.game_phase.name)
        print("type: game_status",type(game_status),game_status)
        print("type: self.level.game_phase.name",type(self.level.game_phase.name), self.level.game_phase.name)

        # Save turn if game has started
        if self.level.is_game_started:
            turn = etree.SubElement(level, "turn")
            turn.text = str(self.level.turn)
            print("self.level.turn (before):",self.level.turn)
            self.level.turn = turn_nb
            print("self.level.turn (after):",self.level.turn)
            # self.level.turn = 5

        # Save current entities stats and position
        entities = self._save_entities(tree_root)
        level.append(entities)

        print("------------------------------------")
        return level

    def _save_entities(self,tree_root):

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
