import pygame as pg

fonts = {
    'BUTTON_FONT': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                    'size': 16},
    'ITEM_FONT': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                  'size': 18},
    'ITEM_FONT_HOVER': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                        'size': 19},
    'ITEM_FONT_STRONG': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                         'size': 18},
    'MISSION_FONT': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                     'size': 20},
    'MENU_SUB_TITLE_FONT': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                            'size': 22},
    'ITEM_DESC_FONT': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                               'size': 24},
    'MENU_TITLE_FONT': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                        'size': 26},
    'TITLE_FONT': {'name': 'fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf',
                   'size': 46},
    'ITALIC_ITEM_FONT': {'name': 'fonts/minya_nouvelle_it.ttf',
                         'size': 14},
    'ITALIC_ITEM_FONT_HOVER': {'name': 'fonts/minya_nouvelle_it.ttf',
                               'size': 16},
    'FPS_FONT': {'default': True}
}


def init_fonts():
    global fonts
    for font in fonts:
        if 'default' in fonts[font]:
            # Use pygame's default font
            fonts[font] = pg.font.SysFont(None, 20, True)
        else:
            fonts[font] = pg.font.Font(fonts[font]['name'], fonts[font]['size'])
