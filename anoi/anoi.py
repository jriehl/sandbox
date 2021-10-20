'''Port and partial rewrite of A Network of Ideas.
'''

import abc
import enum
import itertools
import struct
from typing import Dict, Iterator, Optional, Tuple

import redis


class ANOIReserved(enum.Enum):
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
        self.crnt: int = ANOIReserved.MIN_UNRESERVED.value
        self.uid_map: Dict[int, Dict[int, int]] = {}
        self.uid_content: Dict[int, Tuple[int]] = {}

    def cross(self, uid0: int, uid1: int) -> int:
        uid_map = self.uid_map[uid0]
        self.check(uid1)
        if uid1 in uid_map:
            return uid_map[uid1]
        return ANOIReserved.NIL.value

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
    def __init__(
        self,
        db: Optional[redis.Redis] = None,
        namespace: Optional[str] = None
    ):
        assert len(struct.pack('<I', 0)) == 4
        if db is None:
            db = redis.Redis()
        self.db = db
        self.namespace = (
            namespace.encode() if namespace is not None else b'') + b'_'
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
            return ANOIReserved.NIL.value
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
            crnt = ANOIReserved.MIN_UNRESERVED.value
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


class ANOISimpleTrie:
    def __init__(self, space: ANOISpace, root: int):
        self.space = space
        self.root = root

    def create_node(self, prev_uid: int, key_uid: int) -> int:
        ret_val = self.space.get_uid()
        self.space.cross_equals(prev_uid, key_uid, ret_val)
        return ret_val

    def get_name(self, name: str) -> int:
        vec = tuple(ord(cp) for cp in name)
        return self.get_vector(vec)

    def get_vector(self, vec: Tuple[int]) -> int:
        ret_val = ANOIReserved.NIL.value
        if len(vec) > 0:
            NIL = ANOIReserved.NIL.value
            cross = self.space.cross
            ret_val = cross(self.root, vec[0])
            i = 1
            while (i < len(vec)) and (ret_val != NIL):
                ret_val = cross(ret_val, vec[i])
                i = i + 1
        return ret_val

    def has_name(self, name: str) -> bool:
        vec = tuple(ord(cp) for cp in name)
        return self.get_vector(vec) != ANOIReserved.NIL.value

    def set_name(self, name: str, uid: int) -> int:
        vec = tuple(ord(cp) for cp in name)
        return self.set_vector(vec, uid)

    def set_vector(self, vec: Tuple[int], uid: int) -> int:
        ret_val = ANOIReserved.NIL.value
        if len(vec) == 0:
            raise ValueError('Empty vector cannot map to anything.')
        else:
            cross = self.space.cross
            cross_eq = self.space.cross_equals
            NIL = ANOIReserved.NIL.value
            crnt_uid = self.root
            # Handle vec[i - 1] x vec[i]
            i = 0
            while (i < (len(vec) - 1)) and (crnt_uid != NIL):
                prev_uid = crnt_uid
                crnt_uid = cross(crnt_uid, vec[i])
                i = i + 1
            if crnt_uid == NIL:
                # We had a miss and need to back up one.
                i = i - 1
                crnt_uid = prev_uid
                while (i < (len(vec) - 1)):
                    crnt_uid = self.create_node(crnt_uid, vec[i])
                    i = i + 1
            cross_eq(crnt_uid, vec[-1], uid)
            ret_val = uid
        return ret_val


class ANOITrie(ANOISimpleTrie):
    def __init__(self, base: ANOISimpleTrie, root: int):
        self.base = base
        assert self.base.has_name('REF')
        assert self.base.has_name('PARENT')
        self.space = self.base.space
        self.root = root
        self.ref = self.base.get_name('REF')
        self.parent = self.base.get_name('PARENT')

    def compress_iter(self, uid_vec: Tuple[int]) -> Iterator[int]:
        cross = self.space.cross
        NIL = ANOIReserved.NIL.value
        i = 0
        uid_vec_len = len(uid_vec)
        while i < uid_vec_len:
            crnt_uid = cross(self.root, uid_vec[i])
            last_good_ref = NIL
            last_good_pos = i
            j = i + 1
            while (j < uid_vec_len) and (NIL != crnt_uid):
                crnt_ref = cross(crnt_uid, self.ref)
                if NIL != crnt_ref:
                    last_good_ref = crnt_ref
                    last_good_pos = j
                crnt_uid = cross(crnt_uid, uid_vec[j])
                j = j + 1
            if last_good_ref == NIL:
                # We got nothing, so yield the first UID...
                yield uid_vec[i]
                i = i + 1
            else:
                # Yield the largest match we found...
                yield last_good_ref
                i = last_good_pos

    def compress(self, uid_vec: Tuple[int]) -> Tuple[int]:
        return tuple(self.compress_iter(uid_vec))

    def create_node(self, prev_uid, key_uid):
        ret_val = self.space.get_uid()
        # The Python 2 version of this explicitly set ret_val x REF to NIL,
        # but this is redundant since the cross method returns NIL if the
        # result of UID x REF isn't found.
        self.space.cross_equals(ret_val, self.parent, prev_uid)
        self.space.cross_equals(prev_uid, key_uid, ret_val)
        return ret_val

    def get_vector(self, vec: Tuple[int]) -> int:
        '''Gets ROOT x vec[0] x vec[1] x ... x vec[n-1] x REF.'''
        return super().get_vector(tuple(itertools.chain(vec, (self.ref,))))

    def set_vector(self, vec: Tuple[int], uid: int) -> int:
        '''Sets ROOT x vec... x REF = uid.'''
        return super().set_vector(
            tuple(itertools.chain(vec, (self.ref,))), uid)
