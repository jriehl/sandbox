import threading
import time
from typing import Callable, List, Optional
from pygame import midi

class MidiWrapper:
    def __init__(self):
        midi.init()
        self.devices = midi.get_count()
        self.device_info = [midi.get_device_info(i) for i in range(self.devices)]
        self.default_input = midi.Input(midi.get_default_input_id())
        self.default_output = midi.Output(midi.get_default_output_id())


MIDI: Optional['MidiWrapper'] = None


class InputWrapper:
    def __init__(self, input_device: Optional[midi.Input] = None, handler: Optional[Callable] = None) -> None:
        self.input_device = input_device if input_device is not None else MIDI.default_input
        self.handler = handler if handler is not None else print
        self.cancel_loop = threading.Event()

    def input_loop(self):
        while not self.cancel_loop.is_set():
            while self.input_device.poll():
                events = self.input_device.read(1)
                self.handler(events[0])
            time.sleep(0.0025)
        self.cancel_loop.clear()


def smilify():
    result = []
    for col in range(2, 6):
        result.append(col)
        result.append(112 + col)
    for row in range(2,6):
        left_key = row << 4
        result.append(left_key)
        result.append(left_key + 7)
        if row == 2 or row == 4:
            result.append(left_key + 2)
            result.append(left_key + 5)
        elif row == 5:
            result.append(left_key + 3)
            result.append(left_key + 4)
    for key in (17, 22, 97, 102):
        result.append(key)
    result.sort()
    return tuple(result)


# Static Launchpad smiley key data == smilify()
SMILEY = (2, 3, 4, 5, 17, 22, 32, 34, 37, 39, 48, 55, 64, 66, 69, 71, 80, 83, 84, 87,
    97, 102, 114, 115, 116, 117)


class Launchpad:
    def __init__(self, input_id: Optional[int] = None, output_id: Optional[int] = None) -> None:
        self.input = midi.Input(input_id) if input_id is not None else MIDI.default_input
        self.output = midi.Output(output_id) if output_id is not None else MIDI.default_output
        self.wrapper = InputWrapper(self.input, self.handler)

    def key_xy(self, row: int, col: int) -> int:
        return (row * 16) + col

    def key_clear(self, key: int):
        self.output.write_short(144, key, 0)

    def key_down(self, key: int):
        self.key_red(key)

    def key_up(self, key: int):
        if key in SMILEY:
            self.key_amber(key)
        else:
            self.key_clear(key)

    def key_amber(self, key: int):
        self.output.write_short(144, key, 63)

    def key_green(self, key: int):
        self.output.write_short(144, key, 60)

    def key_red(self, key: int):
        self.output.write_short(144, key, 3)
    
    def smiley(self):
        for key in SMILEY:
            self.key_amber(key)

    def handler(self, event_data: List[List[int]|int]):
        midi_input, clock = event_data
        msg_type, data1, data2, data3 = midi_input
        if msg_type == 144:
            key = data1
            velocity = data2
            if velocity > 0:
                self.key_down(key)
            else:
                self.key_up(key)
        else:
            print(msg_type, data1, data2, data3)


if __name__ == '__main__':
    MIDI = MidiWrapper()
    lp = Launchpad()
    lp.smiley()
    lp.wrapper.input_loop()
