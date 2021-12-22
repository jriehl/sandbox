import unittest

import redis

from .. import anoi


redis_client = None

def check_redis(*args, **kws):
    global redis_client
    if redis_client is None:
        try:
            redis_client_test = redis.Redis(*args, **kws)
            redis_client_test.get('😏')
        except redis.ConnectionError:
            return False
        redis_client = redis_client_test
    return True


class TestANOISpaces(unittest.TestCase):
    def _check_space(self, space: anoi.ANOISpace):
        uid0 = space.get_uid()
        uid1 = space.get_uid()
        uid2 = space.get_uid()
        self.assertNotEqual(uid0, uid1)
        self.assertNotEqual(uid0, uid2)
        self.assertNotEqual(uid1, uid2)
        NIL = anoi.ANOIReserved.NIL.value
        self.assertEqual(space.cross(uid0, uid1), NIL)
        self.assertEqual(space.cross(uid1, uid0), NIL)
        self.assertEqual(space.cross(uid0, uid2), NIL)
        self.assertEqual(space.cross(uid2, uid0), NIL)
        self.assertEqual(space.cross(uid1, uid2), NIL)
        self.assertEqual(space.cross(uid2, uid1), NIL)
        empty = tuple()
        self.assertEqual(space.get_content(uid0), empty)
        self.assertEqual(space.get_content(uid1), empty)
        self.assertEqual(space.get_content(uid2), empty)
        test_tuple = tuple(ord(cp) for cp in 'test_tuple')
        space.set_content(uid0, test_tuple)
        self.assertEqual(space.get_content(uid0), test_tuple)
        self.assertEqual(space.get_content(uid1), empty)
        self.assertEqual(space.get_content(uid2), empty)
        space.set_content(uid0, empty)
        space.set_content(uid1, test_tuple)
        self.assertEqual(space.get_content(uid0), empty)
        self.assertEqual(space.get_content(uid1), test_tuple)
        self.assertEqual(space.get_content(uid2), empty)
        space.cross_equals(uid0, uid1, uid2)
        self.assertEqual(space.cross(uid0, uid1), uid2)
        self.assertEqual(space.cross(uid1, uid0), NIL)
        self.assertEqual(space.cross(uid0, uid2), NIL)
        self.assertEqual(space.cross(uid2, uid0), NIL)
        self.assertEqual(space.cross(uid1, uid2), NIL)
        self.assertEqual(space.cross(uid2, uid1), NIL)
        self.assertEqual(space.get_keys(uid0), (uid1,))
        self.assertEqual(space.get_keys(uid1), empty)
        self.assertEqual(space.get_keys(uid2), empty)
        space.free_uid(uid0)
        space.free_uid(uid1)
        space.free_uid(uid2)
        self.assertRaises(ValueError, space.check, uid0)
        self.assertRaises(ValueError, space.check, uid1)
        self.assertRaises(ValueError, space.check, uid2)
        # TODO: Test validate().

    def test_inmemory_space(self):
        self._check_space(anoi.ANOIInMemorySpace())

    @unittest.skipUnless(check_redis(), 'No Redis server found.')
    def test_redis_space(self):
        self._check_space(anoi.ANOIRedis32Space(redis_client, 'XXX_test'))


class TestANOITrie(unittest.TestCase):
    def test_trie_and_compress(self):
        space = anoi.ANOIInMemorySpace()
        trie = anoi.ANOITrie(space)
        uid0 = space.get_uid()
        uid1 = space.get_uid()
        uid2 = space.get_uid()
        uid3 = space.get_uid()
        uid4 = space.get_uid()
        vec0 = uid0, uid1
        vec1 = uid1, uid2
        vec2 = uid2, uid0
        vec3 = uid0, uid1, uid2
        NIL = anoi.ANOIReserved.NIL.value
        self.assertEqual(trie.get_vector(vec0), NIL)
        self.assertEqual(trie.get_vector(vec1), NIL)
        self.assertEqual(trie.get_vector(vec2), NIL)
        self.assertEqual(trie.get_vector(vec3), NIL)
        self.assertRaises(ValueError, trie.set_vector, (), uid0)
        # XXX: Not sure what set_vector() should return, but going to test
        # what's already there for now.
        self.assertEqual(trie.set_vector(vec0, uid0), uid0)
        self.assertEqual(trie.set_vector(vec1, uid1), uid1)
        self.assertEqual(trie.set_vector(vec2, uid2), uid2)
        self.assertEqual(trie.set_vector(vec3, uid3), uid3)
        self.assertEqual(trie.get_vector(vec0), uid0)
        self.assertEqual(trie.get_vector(vec1), uid1)
        self.assertEqual(trie.get_vector(vec2), uid2)
        self.assertEqual(trie.get_vector(vec3), uid3)
        self.assertIn(trie.root, space.get_keys(uid0))
        self.assertIn(trie.root, space.get_keys(uid1))
        self.assertIn(trie.root, space.get_keys(uid2))
        self.assertIn(trie.root, space.get_keys(uid3))
        test_dict = {
            'a': uid0, 'b': uid1, 'cd': uid2, 'cde': uid3, 'cdf': uid4}
        for name in test_dict.keys():
            self.assertFalse(trie.has_name(name))
        for name, uid in test_dict.items():
            self.assertEqual(trie.set_name(name, uid), uid)
        for name in test_dict.keys():
            self.assertTrue(trie.has_name(name))
        self.assertFalse(trie.has_name('c'))
        self.assertFalse(trie.has_name('cdd'))
        self.assertFalse(trie.has_name('ab'))
        self.assertFalse(trie.has_name('g'))
        for name, uid in test_dict.items():
            self.assertEqual(trie.get_name(name), uid)
        self.assertEqual(anoi.compress(trie, vec3), (uid3, ))


if __name__ == '__main__':
    unittest.main()
