import threading
from pygame import display, event, mixer
import pygame

try:
    from . import midiplay, mixerplay
except ImportError:
    import midiplay, mixerplay


class LaunchBoard(midiplay.Launchpad):
    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.board = mixerplay.SoundBoard(64)
        self.events = [event.custom_type() for _ in range(64)]

    def key_up(self, key: int):
        row = key >> 4
        col = key & 15
        if col < 8:
            super().key_up(key)
            if self.state[key]:
                index = (row << 3) + col
                channel = self.board.play(index)
                if channel is not None:
                    channel.set_endevent(self.events[index])
        else:
            self.key_clear(key)
            volume = 1.0 - (row / 7)
            print(f'Volume is {volume}')
            for sound in self.board.sounds:
                if sound is not None:
                    sound.set_volume(volume)

    def event_loop(self):
        input_thread = threading.Thread(target=self.wrapper.input_loop)
        try:
            input_thread.start()
            while True:
                lb_event = event.wait()
                print(lb_event)
                if lb_event.type < pygame.USEREVENT:
                    if lb_event.type == pygame.KEYDOWN:
                        if lb_event.key == pygame.K_ESCAPE:
                            break
                else:
                    index = None
                    try:
                        index = self.events.index(lb_event.type)
                        row = index >> 3
                        col = index & 7
                        super().key_up((row << 4) + col)
                    except ValueError:
                        pass
        finally:
            self.wrapper.cancel_loop.set()


if __name__ == '__main__':
    display.init()
    display.set_mode([1,1])
    mixerplay.mixer.init()
    midiplay.MIDI = midiplay.MidiWrapper()
    lb = LaunchBoard()
    lb.smiley()
    lb.board.sounds[0] = mixer.Sound('/Users/jon/Music/deafbeef/output.wav')
    lb.event_loop()
