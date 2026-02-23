class Screen:
    """Base interface for screens."""
    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass