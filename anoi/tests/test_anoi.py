import unittest

import redis

import anoi


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


if __name__ == '__main__':
    unittest.main()
