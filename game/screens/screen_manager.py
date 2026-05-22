# screens/screen_manager.py
from __future__ import annotations
from typing import Callable, Dict
from screens.menu import MenuScreen
from screens.game import GameScreen
from screens.configure import ConfigureScreen
from screens.layout_config import LayoutConfigScreen
from screens.robot_config import RobotConfigScreen
from screens.remove_obstacle import RemoveObstacleScreen


class ScreenManager:
    """
    Owns the currently active screen and handles switching between screens.
    Keeps app.py clean and makes adding screens easy.
    """

    def __init__(self, quit_game, fonts):
        self._quit_game = quit_game
        self._fonts = fonts
        self._screens : Dict[str, Screen] = {}
        self._current_name = None
        
        # Register screens here (or expose register() if you prefer)
        self._screens["menu"] = MenuScreen(self, quit_game, fonts)
        self._screens["game"] = GameScreen(self, fonts)
        self._screens["configure"] = ConfigureScreen(self, fonts)
        self._screens["layout_config"] = LayoutConfigScreen(self, fonts)
        self._screens["robot_config"] = RobotConfigScreen(self, fonts)
        self._screens["remove_obstacle"] = RemoveObstacleScreen(self, fonts)

        self.go_to("menu")

    def go_to(self, name: str) -> None:
        if name not in self._screens:
            raise ValueError(f"Unknown screen: {name}")
        self._current_name = name

    @property
    def current(self) -> Screen:
        if self._current_name is None:
            raise RuntimeError("ScreenManager has no active screen.")
        return self._screens[self._current_name]