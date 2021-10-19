'''Port and partial rewrite of A Network of Ideas.
'''

import abc
import enum
import struct
from typing import Dict, Optional, Tuple

import redis


class ANOIAtoms(enum.Enum):
    NIL = 0x0  # None, by any other name...
    POS = 0xe000  # Start of private-use Unicode code points (up to 0xf8ff).
    NEG = 0xe001
    PARENT = 0xe002
    REF = 0xe003
    TIME = 0xe004
    MIN_UNRESERVED = 0x110000 # One more than last Unicode code point...


class ANOISpace(abc.ABC):
    def check(self, uid: int) -> None:
        '''Utility to check that given UID is valid.'''
        if not self.is_valid(uid):
            raise ValueError(f'UID {uid} is not valid.')

    def cross(self, uid0: int, uid1: int) -> int:
        '''Returns uid0 x uid1.'''
        raise NotImplementedError()

    def cross_equals(self, uid0: int, uid1: int, uid2: int) -> None:
        '''Sets uid0 x uid1 = uid2.'''
        raise NotImplementedError()

    def free_uid(self, uid: int) -> None:
        '''Marks UID argument as no longer in use.'''
        raise NotImplementedError()

    def get_content(self, uid: int) -> Tuple[int]:
        '''Returns the contents associated with the given UID.'''
        raise NotImplementedError()

    def get_keys(self, uid: int) -> Tuple[int]:
        '''Get a list of valid cross product arguments.'''
        raise NotImplementedError()

    def get_uid(self) -> int:
        '''Returns a free UID.'''
        raise NotImplementedError()

    def is_valid(self, uid: int) -> bool:
        '''Returns true if the given UID is defined, false otherwise.'''
        raise NotImplementedError()

    def set_content(self, uid: int, content: Tuple[int]) -> None:
        '''Associates the given content with a UID.'''
        raise NotImplementedError()


class ANOIInMemorySpace(ANOISpace):
    def __init__(self) -> None:
        super().__init__()
        self.crnt: int = ANOIAtoms.MIN_UNRESERVED.value
        self.uid_map: Dict[int, Dict[int, int]] = {}
        self.uid_content: Dict[int, Tuple[int]] = {}

    def cross(self, uid0: int, uid1: int) -> int:
        uid_map = self.uid_map[uid0]
        self.check(uid1)
        if uid1 in uid_map:
            return uid_map[uid1]
        return ANOIAtoms.NIL.value

    def cross_equals(self, uid0: int, uid1: int, uid2: int) -> None:
        self.check(uid0)
        self.check(uid1)
        self.check(uid2)
        uid_map = self.uid_map[uid0]
        uid_map[uid1] = uid2

    def free_uid(self, uid: int) -> None:
        self.check(uid)
        del self.uid_map[uid]
        del self.uid_content[uid]

    def get_content(self, uid: int) -> Tuple[int]:
        self.check(uid)
        return self.uid_content[uid]

    def get_keys(self, uid: int) -> Tuple[int]:
        self.check(uid)
        return tuple(self.uid_map[uid].keys())

    def get_uid(self) -> int:
        while self.is_valid(self.crnt):
            self.crnt += 1
        result = self.crnt
        self.uid_map[result] = {}
        self.uid_content[result] = ()
        self.crnt += 1
        return result

    def is_valid(self, uid: int) -> bool:
        return (uid in self.uid_map) and (uid in self.uid_content)

    def set_content(self, uid: int, content: Tuple[int]) -> None:
        self.check(uid)
        self.uid_content[uid] = content


class ANOIRedis32Space(ANOISpace):
    def __init__(self, db: Optional[redis.Redis] = None, namespace: Optional[str] = None):
        assert len(struct.pack('<I', 0)) == 4
        if db is None:
            db = redis.Redis()
        self.db = db
        self.namespace = (namespace.encode() if namespace is not None else b'') + b'_'
        self.content_key = self.namespace + b'content'
        self.crnt_key = self.namespace + b'crnt'

    @staticmethod
    def itob(integer: int) -> bytes:
        return struct.pack('<I', integer)

    @staticmethod
    def istob(uid_vec: Tuple[int]) -> bytes:
        return struct.pack(f'<{len(uid_vec)}I', *uid_vec)

    @ staticmethod
    def btoi(byte_vec: bytes) -> int:
        return struct.unpack('<I', byte_vec)[0]

    @staticmethod
    def btois(byte_vec: bytes) -> Tuple[int]:
        vec_len = len(byte_vec) >> 2
        return struct.unpack(f'<{vec_len}I', byte_vec)

    def cross(self, uid0: int, uid1: int) -> int:
        uid0_key = self.namespace + self.itob(uid0)
        uid1_bytes = self.itob(uid1)
        result = self.db.hget(uid0_key, uid1_bytes)
        if result is None or len(result) != 4:
            raise ValueError(f'Operation {uid0} x {uid1} failed')
        return self.btoi(result)

    def cross_equals(self, uid0: int, uid1: int, uid2: int) -> None:
        uid0_key = self.namespace + self.itob(uid0)
        uid1_bytes = self.itob(uid1)
        uid2_bytes = self.itob(uid2)
        result = self.db.hset(uid0_key, uid1_bytes, uid2_bytes)
        assert result == 1, f'Operation {uid0} x {uid1} = {uid2} failed'

    def free_uid(self, uid: int) -> None:
        uid_bytes = self.itob(uid)
        uid_key = self.namespace + uid_bytes
        self.db.delete(uid_key)
        self.db.hdel(self.content_key, uid_bytes)

    def get_content(self, uid: int) -> Tuple[int]:
        uid_bytes = self.itob(uid)
        result = self.db.hget(self.content_key, uid_bytes)
        if result is None:
            raise ValueError(f'UID {uid} contents not found')
        return self.btois(result)

    def get_keys(self, uid: int) -> Tuple[int]:
        uid_key = self.namespace + self.itob(uid)
        result = self.db.hkeys(uid_key)
        return tuple(self.btoi(value) for value in result)

    def get_uid(self) -> int:
        if self.db.exists(self.crnt_key) != 1:
            crnt = ANOIAtoms.MIN_UNRESERVED.value
            self.db.set(self.crnt_key, crnt)
        else:
            crnt = int(self.db.get(self.crnt_key))
        while self.is_valid(crnt):
            crnt = self.db.incr(self.crnt_key)
        crnt_bytes = self.itob(crnt)
        self.db.hset(self.content_key, crnt_bytes, b'')
        return crnt

    def is_valid(self, uid: int) -> bool:
        uid_bytes = self.itob(uid)
        return self.db.hexists(self.content_key, uid_bytes)

    def set_content(self, uid: int, content: Tuple[int]) -> None:
        self.check(uid)
        self.db.hset(self.content_key, self.istob(content))
