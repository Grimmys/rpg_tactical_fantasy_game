"""
Define FadeInOutAnimation class, a specific animation responsible for progressively displaying and hiding a frame
"""

from src.gui.animation import Animation, Frame

OPACITY_CHANGE_BY_STEP = 5
DEFAULT_DELAY_BETWEEN_STEPS = 10


class FadeInOutAnimation(Animation):
    """
    This animation requires only one frame, and consists on slowly displaying it until it is fully visible.
    At this point, after a few ticks, the frame will slowly disappear.

    Keyword arguments:
    frame -- the frame that should be displayed
    visibility_duration -- the time during which the frame should stay fully visible before starting to disappear

    Attributes:
    visibility_duration -- the time during which the frame should stay fully visible before starting to disappear
    is_fade_in_finished -- whether the animation has already fully displayed the frame or not
    current_opacity -- the current visibility of the frame
    """

    def __init__(self, frame: Frame, visibility_duration: int) -> None:
        super().__init__([frame], DEFAULT_DELAY_BETWEEN_STEPS)
        self.visibility_duration = visibility_duration
        self.is_fade_in_finished: bool = False
        self.current_opacity = 0
        self.current_frame.surface.set_alpha(self.current_opacity)

    def animate(self) -> bool:
        """
        Decrement the timer and check if the opacity of the frame should be changed.

        Return whether the animation is ended or not.
        """
        is_animation_ended = False
        self.timer -= 1

        if self.timer == 0:
            is_animation_ended = self._process_next_animation_step()

        return is_animation_ended

    def _process_next_animation_step(self):
        if self.is_fade_in_finished:
            if self.current_opacity <= 0:
                return True
            self.current_opacity -= OPACITY_CHANGE_BY_STEP
        else:
            self.current_opacity += OPACITY_CHANGE_BY_STEP
            if self.current_opacity >= 255:
                self.current_opacity = 255
                self.is_fade_in_finished = True

        self.current_frame.surface.set_alpha(self.current_opacity)
        self.timer = (
            self.current_frame.duration
            if self.current_opacity != 255
            else self.visibility_duration
        )

        return False
