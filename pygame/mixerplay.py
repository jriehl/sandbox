from typing import Iterable, List, Mapping, Optional
from pygame import mixer


class SoundBoard:
    def __init__(self, size: int = 64):
        self.size = size
        self.sounds: List[Optional[mixer.Sound]] = [None] * size

    def update(self, mapping: Optional[Mapping[int, Optional[mixer.Sound | str]]] = None):
        if mapping is not None:
            for index, sound in mapping.items():
                if isinstance(sound, str):
                    sound = mixer.Sound(sound)
                self.sounds[index] = sound

    @classmethod
    def from_mapping(cls, mapping: Mapping[int, Optional[mixer.Sound | str]]):
        size = max(mapping.keys()) + 1
        result = cls(size)
        result.update(mapping)
        return result

    @classmethod
    def from_iterable(cls, iterable: Iterable[Optional[mixer.Sound | str]]):
        return cls.from_mapping({index: sound for index, sound in enumerate(iterable)})

    def play(self, index: int, *args, **kws) -> Optional[mixer.Channel]:
        if index < 0 or index > (self.size - 1):
            raise ValueError(f'{index} is out of range')
        sound = self.sounds[index]
        if sound is not None:
            return sound.play(*args, **kws)
        return None
