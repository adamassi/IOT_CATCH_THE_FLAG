# screens/screen_manager.py
from __future__ import annotations
from typing import Callable, Dict

from screens.base import Screen
from screens.menu import MenuScreen
from screens.game import GameScreen


class ScreenManager:
    """
    Owns the currently active screen and handles switching between screens.
    Keeps app.py clean and makes adding screens easy.
    """

    def __init__(self, quit_game: Callable[[], None], fonts: dict):
        self._quit_game = quit_game
        self._fonts = fonts
        self._screens: Dict[str, Screen] = {}
        self._current_name: str | None = None

        # Register screens here (or expose register() if you prefer)
        self._screens["menu"] = MenuScreen(self, quit_game=self._quit_game, fonts=self._fonts)
        self._screens["game"] = GameScreen(self, fonts=self._fonts)

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