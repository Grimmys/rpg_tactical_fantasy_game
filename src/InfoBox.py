from src.fonts import *
from src.constants import *
from src.TextElement import TextElement
from src.Button import Button
from src.DynamicButton import DynamicButton
from src.ItemButton import ItemButton
from src.Menus import GenericActions

BUTTON_INACTIVE = "imgs/interface/MenuButtonInactiv.png"
BUTTON_ACTIVE = "imgs/interface/MenuButtonPreLight.png"

CLOSE_BUTTON_MARGINTOP = 20

DEFAULT_WIDTH = 400


class InfoBox:
    def __init__(self, name, type_id, sprite, entries, width=DEFAULT_WIDTH, el_rect_linked=None, close_button=0,
                 sep=False, title_color=WHITE):
        self.name = name
        self.type = type_id
        self.element_linked = el_rect_linked
        self.close_button = close_button
        self.title_color = title_color
        self.sep = {'display': sep,
                    'posY': 0,
                    'height': 0}
        self.entries = entries

        self.elements = self.init_elements(self.entries, width)
        height = self.determine_height(close_button)
        self.size = (width, height)
        self.pos = self.determine_pos()

        self.sep['height'] += self.size[1]

        if self.pos:
            self.determine_elements_pos()
        self.buttons = self.find_buttons()

        self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), self.size)

    def init_elements(self, entries, width):
        elements = []
        for row in entries:
            element = []
            for entry in row:
                if 'margin' not in entry:
                    entry['margin'] = (0, 0, 0, 0)

                if entry['type'] == 'button':
                    name = fonts['BUTTON_FONT'].render(entry['name'], 1, WHITE)
                    sprite = pg.transform.scale(pg.image.load(BUTTON_INACTIVE).convert_alpha(), BUTTON_SIZE)
                    sprite.blit(name, (sprite.get_width() // 2 - name.get_width() // 2,
                                       sprite.get_height() // 2 - name.get_height() // 2))
                    sprite_hover = pg.transform.scale(pg.image.load(BUTTON_ACTIVE).convert_alpha(), BUTTON_SIZE)
                    sprite_hover.blit(name, (sprite_hover.get_width() // 2 - name.get_width() // 2,
                                             sprite_hover.get_height() // 2 - name.get_height() // 2))
                    if 'args' not in entry:
                        entry['args'] = []

                    element.append(Button(entry['id'], entry['args'], BUTTON_SIZE, (0, 0), sprite, sprite_hover,
                                          entry['margin']))
                elif entry['type'] == 'parameter_button':
                    name = fonts['ITEM_FONT'].render(entry['name'] + ' ' + entry['values'][entry['current_value_ind']]['label'],
                                            1, WHITE)
                    base_sprite = pg.transform.scale(pg.image.load(BUTTON_INACTIVE).convert_alpha(), BUTTON_SIZE)
                    sprite = base_sprite.copy()
                    sprite.blit(name, (base_sprite.get_width() // 2 - name.get_width() // 2,
                                       base_sprite.get_height() // 2 - name.get_height() // 2))
                    base_sprite_hover = pg.transform.scale(pg.image.load(BUTTON_ACTIVE).convert_alpha(), BUTTON_SIZE)
                    sprite_hover = base_sprite_hover.copy()
                    sprite_hover.blit(name, (base_sprite_hover.get_width() // 2 - name.get_width() // 2,
                                             base_sprite_hover.get_height() // 2 - name.get_height() // 2))
                    element.append(DynamicButton(entry['id'], [], BUTTON_SIZE, (0, 0), sprite, sprite_hover,
                                                 entry['margin'], entry['values'], entry['current_value_ind'],
                                                 entry['name'], base_sprite, base_sprite_hover))
                elif entry['type'] == 'text_button':
                    name = fonts['ITEM_FONT'].render(entry['name'], 1, entry['color'])
                    name_hover = fonts['ITEM_FONT'].render(entry['name'], 1, entry['color_hover'])
                    if 'obj' not in entry:
                        entry['obj'] = None
                    element.append(Button(entry['id'], [], name.get_size(), (0, 0), name, name_hover, entry['margin'],
                                          entry['obj']))

                elif entry['type'] == 'item_button':
                    button_size = ITEM_BUTTON_SIZE
                    disabled = 'disabled' in entry
                    if 'subtype' in entry:
                        if entry['subtype'] == 'trade':
                            button_size = TRADE_ITEM_BUTTON_SIZE
                    if 'price' not in entry:
                        entry['price'] = 0
                    if 'args' not in entry:
                        entry['args'] = []
                    element.append(ItemButton(entry['id'], entry['args'], button_size, (0, 0), entry['item'], entry['margin'],
                                              entry['index'], entry['price'], disabled))
                elif entry['type'] == 'text':
                    if 'font' not in entry:
                        entry['font'] = fonts['ITEM_FONT']
                    if 'color' not in entry:
                        entry['color'] = WHITE
                    element.append(TextElement(entry['text'], width, (0, 0), entry['font'],
                                               entry['margin'], entry['color']))
            elements.append(element)
        title = TextElement(self.name, width, (0, 0), fonts['MENU_TITLE_FONT'], (len(entries), 0, 20, 0),
                            self.title_color)
        self.sep['posY'] += title.get_height()
        elements.insert(0, [title])
        return elements

    def determine_height(self, close_button):
        # Margin to be add at begin and at end
        height = MARGIN_BOX * 2
        self.sep['height'] -= height
        self.sep['posY'] += height
        for row in self.elements:
            max_height = 0
            for el in row:
                el_height = el.get_height() + MARGIN_TOP
                if el_height > max_height:
                    max_height = el_height
            height += max_height
            row.insert(0, max_height)
        if close_button > 0:
            close_button_height = CLOSE_BUTTON_SIZE[1] + MARGIN_TOP + CLOSE_BUTTON_MARGINTOP
            height += close_button_height
            self.sep['height'] -= close_button_height

            # Button sprites
            name = fonts['ITEM_FONT'].render("Close", 1, WHITE)
            sprite = pg.transform.scale(pg.image.load(BUTTON_INACTIVE).convert_alpha(), CLOSE_BUTTON_SIZE)
            sprite.blit(name, (sprite.get_width() // 2 - name.get_width() // 2,
                               sprite.get_height() // 2 - name.get_height() // 2))
            sprite_hover = pg.transform.scale(pg.image.load(BUTTON_ACTIVE).convert_alpha(), CLOSE_BUTTON_SIZE)
            sprite_hover.blit(name, (sprite_hover.get_width() // 2 - name.get_width() // 2,
                                     sprite_hover.get_height() // 2 - name.get_height() // 2))

            self.elements.append([close_button_height,
                                  Button(GenericActions.CLOSE, [close_button], CLOSE_BUTTON_SIZE, (0, 0), sprite,
                                         sprite_hover, (CLOSE_BUTTON_MARGINTOP, 0, 0, 0))])
        return height

    def determine_pos(self):
        if self.element_linked:
            pos = [self.element_linked.x + self.element_linked.width,
                   self.element_linked.y + self.element_linked.height - self.size[1] // 2]
            if pos[1] < 0:
                pos[1] = 0
            elif pos[1] + self.size[1] > MAX_MAP_HEIGHT:
                pos[1] = MAX_MAP_HEIGHT - self.size[1]
            if pos[0] + self.size[0] > MAX_MAP_WIDTH:
                pos[0] = self.element_linked.x - self.size[0]
            return pos
        return []

    def get_type(self):
        return self.type

    def find_buttons(self):
        buttons = []
        for row in self.elements:
            for el in row[1:]:
                if isinstance(el, Button):
                    buttons.append(el)
        return buttons

    def determine_elements_pos(self):
        y = self.pos[1] + MARGIN_BOX
        # Memorize mouse position in case it is over a button
        mouse_pos = pg.mouse.get_pos()
        # A row begins by a value identifying its height, followed by its elements
        for row in self.elements:
            nb_elements = len(row) - 1
            i = 1
            for el in row[1:]:
                base_x = self.pos[0] + (self.size[0] // (2 * nb_elements)) * i
                x = base_x - el.get_width() // 2
                el.pos = (x, y + el.get_margin_top())
                if isinstance(el, Button):
                    el.set_hover(el.get_rect().collidepoint(mouse_pos))
                i += 2
            y += row[0]

    def update_content(self, entries):
        self.elements = self.init_elements(entries, self.size[0])
        self.determine_height(self.close_button)
        if self.pos:
            self.determine_elements_pos()
        self.buttons = self.find_buttons()

    def display(self, win):
        if self.pos:
            win.blit(self.sprite, self.pos)
        else:
            win_size = win.get_size()
            self.pos = (win_size[0] // 2 - self.size[0] // 2, win_size[1] // 2 - self.size[1] // 2)
            win.blit(self.sprite, self.pos)
            self.determine_elements_pos()

        for row in self.elements:
            for el in row[1:]:
                el.display(win)

        if self.sep['display']:
            pg.draw.line(win, WHITE, (self.pos[0] + self.size[0] / 2, self.pos[1] + self.sep['posY']),
                                     (self.pos[0] + self.size[0] / 2, self.pos[1] + self.sep['height']), 2)

    def motion(self, pos):
        for button in self.buttons:
            button.set_hover(button.get_rect().collidepoint(pos))

    def click(self, pos):
        for button in self.buttons:
            if button.get_rect().collidepoint(pos):
                return button.action_triggered()
        return False
