'''Port and partial rewrite of A Network of Ideas.
'''

import abc
import enum
import functools
import struct
from typing import Any, Dict, Iterator, Optional, Tuple

import redis


class ANOIReserved(enum.Enum):
    NIL = 0x0  # None, by any other name...
    ROOT = 0xe000  # Start of private-use Unicode code points (up to 0xf8ff).
    PARENT = 0xe001
    REF = 0xe002
    MIN_UNRESERVED = 0x110000 # One more than last Unicode code point...


class ANOIBootstrapped(enum.Enum):
    TYPE = enum.auto()
    NAME = enum.auto()
    TIME = enum.auto()
    NEXT = enum.auto()
    PREV = enum.auto()


ANOIReservedSet = set(elem.value for elem in ANOIReserved)


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

    def validate(self, uid: int) -> bool:
        '''Ensure a given UID is valid, returning true if the UID was already
        valid, false otherwise.'''
        raise NotImplementedError()


class ANOIInMemorySpace(ANOISpace):
    def __init__(self) -> None:
        super().__init__()
        self.crnt: int = ANOIReserved.MIN_UNRESERVED.value
        self.uid_map: Dict[int, Dict[int, int]] = {}
        self.uid_content: Dict[int, Tuple[int]] = {}

    def cross(self, uid0: int, uid1: int) -> int:
        self.check(uid0)  # Force a value error before we raise a key error.
        uid_map = self.uid_map[uid0]
        if uid1 in uid_map:
            return uid_map[uid1]
        return ANOIReserved.NIL.value

    def cross_equals(self, uid0: int, uid1: int, uid2: int) -> None:
        self.check(uid0)
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

    def validate(self, uid: int) -> bool:
        if self.is_valid(uid):
            return True
        self.uid_map[uid] = {}
        self.uid_content[uid] = ()
        return False


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
        self.check(uid)
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
        uid_bytes = self.itob(uid)
        content_bytes = self.istob(content)
        self.db.hset(self.content_key, uid_bytes, content_bytes)

    def validate(self, uid: int) -> bool:
        if self.is_valid(uid):
            return True
        uid_bytes = self.itob(uid)
        self.db.hset(self.content_key, uid_bytes, b'')
        return False


def ord_iter(in_str: str) -> Iterator[int]:
    return (ord(ch) for ch in in_str)

def str_to_vec(in_str: str) -> Tuple[int]:
    return tuple(ord_iter(in_str))

def vec_to_str(in_vec: Iterator[int]) -> str:
    return ''.join(map(chr, in_vec))


class ANOITrie:
    def __init__(self, space: ANOISpace, root: int = ANOIReserved.ROOT.value):
        self.space = space
        self.space.validate(root)
        self.root = root

    def create_node(self, prev_uid: int, key_uid: int) -> int:
        ret_val = self.space.get_uid()
        self.space.cross_equals(ret_val, ANOIReserved.PARENT.value, prev_uid)
        self.space.cross_equals(ret_val, ANOIReserved.ROOT.value, self.root)
        self.space.cross_equals(prev_uid, key_uid, ret_val)
        return ret_val

    def get_name(self, name: str) -> int:
        return self.get_vector(str_to_vec(name))

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
            if ret_val != NIL:
                ret_val = cross(ret_val, ANOIReserved.REF.value)
        return ret_val

    def has_name(self, name: str) -> bool:
        return self.get_name(name) != ANOIReserved.NIL.value

    def set_name(self, name: str, uid: int) -> int:
        return self.set_vector(str_to_vec(name), uid)

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
            while (i < len(vec)) and (crnt_uid != NIL):
                prev_uid = crnt_uid
                crnt_uid = cross(crnt_uid, vec[i])
                i = i + 1
            if crnt_uid == NIL:
                # We had a miss and need to back up one.
                i = i - 1
                crnt_uid = prev_uid
                while i < len(vec):
                    crnt_uid = self.create_node(crnt_uid, vec[i])
                    i = i + 1
            cross_eq(crnt_uid, ANOIReserved.REF.value, uid)
            # XXX Not sure I like the following convention, but it allows us
            # to backchain the name for a given trie.
            cross_eq(uid, self.root, crnt_uid)
            ret_val = uid
        return ret_val


def compress_iter(trie: ANOITrie, uid_vec: Tuple[int]) -> Iterator[int]:
    cross = trie.space.cross
    NIL = ANOIReserved.NIL.value
    REF = ANOIReserved.REF.value
    i = 0
    uid_vec_len = len(uid_vec)
    while i < uid_vec_len:
        crnt_uid = cross(trie.root, uid_vec[i])
        last_good_ref = NIL
        last_good_pos = i
        j = i + 1
        while (j <= uid_vec_len) and (NIL != crnt_uid):
            crnt_ref = cross(crnt_uid, REF)
            if NIL != crnt_ref:
                last_good_ref = crnt_ref
                last_good_pos = j
            if j >= uid_vec_len:
                break
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

def compress(trie: ANOITrie, uid_vec: Tuple[int]) -> Tuple[int]:
    return tuple(compress_iter(trie, uid_vec))

def build_root_trie(space: ANOISpace) -> ANOITrie:
    '''Build the boot trie for a space.'''
    root_trie = ANOITrie(space)
    for reserved in ANOIReserved:
        space.validate(reserved.value)
        root_trie.set_name(reserved.name, reserved.value)
    bootstrapped_uids = {bootstrapped.name: space.get_uid()
        for bootstrapped in ANOIBootstrapped}
    name_uid = bootstrapped_uids['NAME']
    type_uid = bootstrapped_uids['TYPE']
    for bootstrapped_name, target_uid in bootstrapped_uids.items():
        root_trie.set_name(bootstrapped_name, target_uid)
        target_name_uid = space.get_uid()
        space.set_content(target_name_uid, str_to_vec(bootstrapped_name))
        space.cross_equals(target_uid, name_uid, target_name_uid)
        space.cross_equals(target_name_uid, type_uid, name_uid)
    return root_trie

@functools.cache
def root_trie(space: ANOISpace) -> ANOITrie:
    # TODO: More type checking than just validity on ROOT atom?
    if not space.is_valid(ANOIReserved.ROOT.value):
        result = build_root_trie(space)
    else:
        result = ANOITrie(space)
    return result


class ANOITrieProxy:
    def __init__(self, trie: ANOITrie):
        super().__setattr__('__trie__', trie)

    def __getattr__(self, name: str) -> int:
        return self.__trie__.get_name(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self.__trie__.set_name(name, int(value))

    def __getitem__(self, item: Any) -> int:
        return self.__trie__.get_name(str(item))

    def __setitem__(self, item: Any, value: Any) -> None:
        self.__trie__.set_name(str(item), int(value))

    @classmethod
    def root(cls, space: ANOISpace):
        return cls(root_trie(space))


class ANOINamespace(ANOITrie):
    def __init__(
        self,
        space: ANOISpace,
        name: str,
        basis_uid: Optional[int] = None
    ):
        self.name = name
        if basis_uid is None:
            basis_trie = root_trie(space)
        else:
            basis_trie = ANOITrie(space, basis_uid)
        self.basis = basis_trie
        self.TYPE = basis_trie.get_name('TYPE')
        self.NAME = basis_trie.get_name('NAME')
        my_root = basis_trie.get_name(name)
        if my_root == ANOIReserved.NIL.value:
            my_root = space.get_uid()
            basis_trie.set_name(name, my_root)
        super().__init__(space, my_root)
        self.name_atom(my_root, name)

    def name_atom(self, atom_uid: int, name: str) -> int:
        result = self.space.cross(atom_uid, self.NAME)
        if result == ANOIReserved.NIL.value:
            result = self.space.get_uid()
            self.space.set_content(result, str_to_vec(name))
            self.space.cross_equals(result, self.TYPE, self.NAME)
            self.space.cross_equals(atom_uid, self.NAME, result)
        return result

    def set_name(self, name: str, uid: int) -> int:
        result = super().set_name(name, uid)
        self.name_atom(result, name)
        return result


@functools.cache
def anoi_types(space: ANOISpace) -> ANOITrieProxy:
    result = ANOITrieProxy(ANOINamespace(space, 'types'))
    for builtin in ('STRING',):
        result[builtin] = space.get_uid()
    return result
