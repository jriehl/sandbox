import threading
import time
from typing import Callable, List, Optional
from typing_extensions import TypeVarTuple
from pygame import midi

midi.init()
devices = midi.get_count()
device_info = [midi.get_device_info(i) for i in range(devices)]
default_input = midi.Input(midi.get_default_input_id())
default_output = midi.Output(midi.get_default_output_id())

class InputWrapper:
    def __init__(self, input_device: Optional[midi.Input] = None, handler: Optional[Callable] = None) -> None:
        self.input_device = input_device if input_device is not None else default_input
        self.handler = handler if handler is not None else print
        self.cancel_loop = threading.Event()

    def input_loop(self):
        while not self.cancel_loop.is_set():
            while self.input_device.poll():
                events = self.input_device.read(1)
                self.handler(events[0])
            time.sleep(0.0025)
        self.cancel_loop.clear()

class Launchpad:
    def __init__(self, input_id: Optional[int] = None, output_id: Optional[int] = None) -> None:
        self.input = midi.Input(input_id) if input_id is not None else default_input
        self.output = midi.Output(output_id) if output_id is not None else default_output
        self.wrapper = InputWrapper(self.input, self.handler)
        self.state = [False] * 144

    def key_xy(self, row: int, col: int) -> int:
        return (row * 16) + col

    def key_clear(self, key: int):
        self.output.write_short(144, key, 0)

    def key_down(self, key: int):
        self.key_red(key)

    def key_up(self, key: int):
        if self.state[key]:
            self.key_clear(key)
            self.state[key] = False
        else:
            self.key_green(key)
            self.state[key] = True

    def key_amber(self, key: int):
        self.output.write_short(144, key, 63)

    def key_green(self, key: int):
        self.output.write_short(144, key, 60)

    def key_red(self, key: int):
        self.output.write_short(144, key, 3)
    
    def smiley(self):
        raise NotImplementedError('lazy developer error')

    def handler(self, event_data: List[List[int]|int]):
        midi_input, clock = event_data
        msg_type, data1, data2, data3 = midi_input
        if msg_type == 144:
            key = data1
            velocity = data2
            print('Note on', key, velocity)
            if velocity > 0:
                self.key_down(key)
            else:
                self.key_up(key)
        else:
            print(msg_type, data1, data2, data3)
