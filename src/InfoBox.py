import pygame as pg

from src.TextElement import TextElement
from src.Button import Button
from src.ItemButton import ItemButton


<<<<<<< HEAD
MENU_TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 26)
=======
TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 26)
>>>>>>> 7acfac91df1e95dce2f8b2478efaa777d8d5a06f
ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 16)
ITEM_DESC_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MARGINTOP = 10
MARGINBOX = 20

TILE_SIZE = 48
MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10

BUTTON_INACTIVE = "imgs/interface/MenuButtonInactiv.png"
BUTTON_ACTIVE = "imgs/interface/MenuButtonPreLight.png"

BUTTON_SIZE = (150, 30)
ITEM_BUTTON_SIZE = (180, TILE_SIZE + 30)
CLOSE_BUTTON_SIZE = (150, 50)
CLOSE_ACTION_ID = -1
<<<<<<< HEAD
CLOSE_BUTTON_MARGINTOP = 20
=======
>>>>>>> 7acfac91df1e95dce2f8b2478efaa777d8d5a06f

DEFAULT_WIDTH = 400


class InfoBox:
    def __init__(self, name, sprite, entries, width=DEFAULT_WIDTH, el_rect_linked=None, close_button=False):
        self.name = name
<<<<<<< HEAD
        self.title = TextElement(self.name, (0, 0), MENU_TITLE_FONT, (0, 0, 0, 0), WHITE)
=======
        self.title = TextElement(self.name, (0, 0), TITLE_FONT, (0, 0, 0, 0), WHITE)
>>>>>>> 7acfac91df1e95dce2f8b2478efaa777d8d5a06f
        self.element_linked = el_rect_linked
        self.close_button = close_button

        self.elements = InfoBox.init_elements(entries, self.title)
        self.determine_sizepos(width, el_rect_linked, close_button)
        self.determine_elements_pos()
        self.buttons = self.get_buttons()

        self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), self.size)


    @staticmethod
    def init_elements(entries, title):
        elements = []
        for row in entries:
            element = []
            for entry in row:
                if 'margin' not in entry:
                    entry['margin'] = (0, 0, 0, 0)
<<<<<<< HEAD
=======

>>>>>>> 7acfac91df1e95dce2f8b2478efaa777d8d5a06f
                if entry['type'] == 'button':
                    element.append(Button(entry['name'], entry['id'], BUTTON_SIZE, (0, 0), BUTTON_INACTIVE, BUTTON_ACTIVE, entry['margin']))
                elif entry['type'] == 'item_button':
                    element.append(ItemButton(ITEM_BUTTON_SIZE, (0, 0), entry['item'], entry['margin'], entry['index']))
                elif entry['type'] == 'text':
                    if 'font' not in entry:
                        entry['font'] = ITEM_FONT
<<<<<<< HEAD
                    if 'color' not in entry:
                        entry['color'] = WHITE
                    element.append(TextElement(entry['text'], (0, 0), entry['font'], entry['margin'], entry['color']))
=======
                    element.append(TextElement(entry['text'], (0, 0), entry['font'], entry['margin']))
>>>>>>> 7acfac91df1e95dce2f8b2478efaa777d8d5a06f
            elements.append(element)
        elements.insert(0, [title])
        return elements

    def determine_sizepos(self, width, el_rect_linked, close_button):
        # Margin to be add at begin and at end
        height = MARGINBOX * 2
        for row in self.elements:
            max_height = 0
            for el in row:
                el_height = el.get_height() + MARGINTOP
                if el_height > max_height:
                    max_height = el_height
            height += max_height
            row.insert(0, max_height)
        if close_button:
<<<<<<< HEAD
            close_button_height = CLOSE_BUTTON_SIZE[1] + MARGINTOP + CLOSE_BUTTON_MARGINTOP
            height += close_button_height
            self.elements.append([close_button_height,
                                  Button("Close", CLOSE_ACTION_ID, CLOSE_BUTTON_SIZE, (0, 0), BUTTON_INACTIVE,
                                         BUTTON_ACTIVE, (CLOSE_BUTTON_MARGINTOP, 0, 0, 0))])
=======
            close_button_height = CLOSE_BUTTON_SIZE[1] + MARGINTOP
            height += close_button_height
            self.elements.append([close_button_height,
                                  Button("Close", CLOSE_ACTION_ID, CLOSE_BUTTON_SIZE, (0, 0), BUTTON_INACTIVE,
                                         BUTTON_ACTIVE, (0, 0, 0, 0))])
>>>>>>> 7acfac91df1e95dce2f8b2478efaa777d8d5a06f

        self.size = (width, height)
        self.pos = self.determine_pos(el_rect_linked)

    def determine_pos(self, el_rect_linked):
        if el_rect_linked:
            pos = [el_rect_linked.x + el_rect_linked.width, el_rect_linked.y + el_rect_linked.height - self.size[1] // 2]
        else:
            pos = [MAP_WIDTH // 2 - self.size[0] // 2, MAP_HEIGHT // 2 - self.size[1] // 2]

        if pos[1] < 0:
            pos[1] = 0
        elif pos[1] + self.size[1] > MAP_HEIGHT:
            pos[1] = MAP_HEIGHT - self.size[1]
        if pos[0] + self.size[0] > MAP_WIDTH:
            pos[0] = el_rect_linked.x - self.size[0]

        return pos

    def get_buttons(self):
        buttons = []
        for row in self.elements:
            for el in row[1:]:
                if isinstance(el, Button):
                    buttons.append(el)
        return buttons

    def determine_elements_pos(self):
        y = self.pos[1] + MARGINBOX
        for row in self.elements:
            base_x = self.pos[0]
            nb_elements = len(row) - 1
            i = 1
            for el in row[1:]:
                base_x += (self.size[0] // (2 * nb_elements)) * i
                x = base_x - el.get_width() // 2
                el.set_pos((x, y + el.get_margin_top()))
                i += 1
            y += row[0]

    def update_content(self, entries):
        self.elements = InfoBox.init_elements(entries, self.title)
        self.determine_sizepos(self.size[0], self.element_linked, self.close_button)
        self.determine_elements_pos()
        self.buttons = self.get_buttons()

    def display(self, win):
        win.blit(self.sprite, self.pos)
        for row in self.elements:
            for el in row[1:]:
                el.display(win)

    def motion(self, pos):
        for button in self.buttons:
            button.set_hover(button.get_rect().collidepoint(pos))

    def click(self, pos):
        for button in self.buttons:
            if button.get_rect().collidepoint(pos):
                return button.action_triggered()
        return False