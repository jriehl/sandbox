import argparse
import threading
import yaml
from pygame import display, event, midi
import pygame

try:
    from . import midiplay, mixerplay
except ImportError:
    import midiplay, mixerplay


class LaunchKeys(midiplay.Launchpad):
    def __init__(self, target_id: int = 2, *args, **kws):
        super().__init__(*args, **kws)
        self.target = midi.Output(target_id)
        self.base_note = 36
        self.velocity = 127

    def key_down(self, key: int):
        super().key_down(key)
        row = key >> 4
        col = key & 15
        if col < 8:
            note = self.base_note + (row * 8) + col
            self.target.note_on(note, self.velocity)

    def key_up(self, key: int):
        if key in midiplay.SMILEY:
            self.key_amber(key)
        else:
            self.key_clear(key)
        row = key >> 4
        col = key & 15
        if col < 8:
            note = self.base_note + (row * 8) + col
            self.target.note_off(note)
        elif row > 1:
            self.velocity = int(127 - ((row - 2) / 5))
            print(f'Velocity is now {self.velocity}')
        else:
            base_note = self.base_note + (-8 if row == 1 else 8)
            if base_note >= 0 and base_note < 63:
                self.base_note = base_note
                print(f'Base MIDI note is now {base_note}')


class LaunchBoard(midiplay.Launchpad):
    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.board = mixerplay.SoundBoard(64)
        self.events = [event.custom_type() for _ in range(64)]
        self.state = [False] * 64

    def toggle_state(self, index: int):
        result = self.state[index]
        self.state[index] ^= True
        return result

    def key_up(self, key: int):
        row = key >> 4
        col = key & 15
        if col < 8:
            index = (row << 3) + col
            old_state = self.toggle_state(index)
            if old_state:
                super().key_up(key)
            else:
                self.key_green(key)
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


major_intervals = 2, 2, 1, 2, 2, 2, 1

def major_key(root):
    return [root + sum(major_intervals[:index]) for index in range(7)]

minor_intervals = 2, 1, 2, 2, 1, 2, 2

def minor_key(root):
    return [root + sum(minor_intervals[:index]) for index in range(7)]


def soundboard(args):
    display.init()
    display.set_mode([1, 1])
    lb = LaunchBoard()
    lb.smiley()
    yaml_doc = yaml.safe_load(args.input[0])
    if not isinstance(yaml_doc, dict):
        raise ValueError('expected YAML object document')
    entries = yaml_doc['entries']
    if len(entries) > 64:
        raise ValueError('YAML list must contain fewer than 65 entries')
    lb.board.update(dict(enumerate(entries)))
    lb.event_loop()


def keyboard(args):
    lk = LaunchKeys()
    lk.smiley()
    lk.wrapper.input_loop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    sb_parser = subparsers.add_parser('soundboard', aliases=['sb', 'sound'])
    sb_parser.add_argument('input', nargs=1, type=open)
    sb_parser.set_defaults(func=soundboard)
    key_parser = subparsers.add_parser('keyboard', aliases=['kb', 'key'])
    key_parser.set_defaults(func=keyboard)
    args = parser.parse_args()
    mixerplay.mixer.init()
    midiplay.MIDI = midiplay.MidiWrapper()
    args.func(args)
