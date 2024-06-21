import unittest

from src.gui.fade_in_out_animation import *
from tests.tools import minimal_setup_for_game
from src.gui.constant_sprites import constant_sprites

class TestFadeInOutAnimation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_fade_in_out(self):
        frame = Frame(constant_sprites["new_turn"], constant_sprites["new_turn_pos"])
        animation = FadeInOutAnimation(frame, 30) 
        self.assertEqual(animation.current_opacity, 0)
        self.assertFalse(animation.is_fade_in_finished)
        
        for _ in range(51):  
            self.assertFalse(animation._process_next_animation_step())

        self.assertEqual(animation.current_opacity, 255)
        self.assertTrue(animation.is_fade_in_finished)
        self.assertEqual(animation.timer, animation.visibility_duration)     

        for _ in range(51):  
            self.assertFalse(animation._process_next_animation_step())   

        self.assertEqual(animation.current_opacity, 0)
        self.assertTrue(animation._process_next_animation_step())    
