class MusicController:
    def __init__(self):
        self.playing = False
        self.current_track = None

    def play(self, track: str = None):
        self.playing = True
        self.current_track = track

    def stop(self):
        self.playing = False
