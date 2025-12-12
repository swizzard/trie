import unittest

from src import MutableTrie, Trie


class TestTrie(unittest.TestCase):
    A_KEY = (1, 2, 3, 4)
    B_KEY = (1, 2, 4)
    C_KEY = (2, 2, 5)
    A = "a"
    B = "b"
    C = "c"
    TERM = 0

    def test_from_items(self):
        key_a_list = list(self.A_KEY)
        key_b_list = list(self.B_KEY)
        key_c_list = list(self.C_KEY)
        items = [(key_a_list, self.A), (key_b_list, self.B), (key_c_list, self.C)]
        trie = Trie.from_items(self.TERM, items)
        self.assertEqual(trie[self.A_KEY], self.A, "A")
        self.assertEqual(trie[self.B_KEY], self.B, "B")
        self.assertEqual(trie[self.C_KEY], self.C, "C")

    def test_from_dict(self):
        dct = {self.A_KEY: self.A, self.B_KEY: self.B, self.C_KEY: self.C}
        trie = Trie.from_dict(self.TERM, dct)
        self.assertEqual(trie[self.A_KEY], self.A, "A")
        self.assertEqual(trie[self.B_KEY], self.B, "B")
        self.assertEqual(trie[self.C_KEY], self.C, "C")

    def test_not_found(self):
        dct = {self.A_KEY: self.A, self.B_KEY: self.B, self.C_KEY: self.C}
        trie = Trie.from_dict(self.TERM, dct)
        bad_key = (1, 2)
        with self.assertRaises(KeyError):
            trie[bad_key]

    def test_get_not_found(self):
        dct = {self.A_KEY: self.A, self.B_KEY: self.B, self.C_KEY: self.C}
        trie = Trie.from_dict(self.TERM, dct)
        bad_key = (1, 2)
        default = "d"
        self.assertEqual(trie.get(bad_key, default), default)

    def test_keys(self):
        dct = {self.A_KEY: self.A, self.B_KEY: self.B, self.C_KEY: self.C}
        trie = Trie.from_dict(self.TERM, dct)
        expected_keys = {1, 2}
        self.assertEqual(set(trie.keys()), expected_keys)

    def test_items(self):
        dct = {self.A_KEY: self.A, self.B_KEY: self.B, self.C_KEY: self.C}
        trie = Trie.from_dict(self.TERM, dct)
        expected_keys = {1, 2}
        for key, subtrie in trie.items():
            expected_keys.remove(key)
            self.assertIsInstance(subtrie, Trie)
            self.assertEqual(subtrie.terminal_marker, trie.terminal_marker)
        self.assertEqual(len(expected_keys), 0)

    def test_get_subtrie(self):
        dct = {self.A_KEY: self.A, self.B_KEY: self.B, self.C_KEY: self.C}
        trie = Trie.from_dict(self.TERM, dct)
        sub_key = (1, 2)
        sub_trie = trie.get_subtrie(sub_key)
        self.assertIsInstance(sub_trie, Trie)
        expected_keys = {3, 4}
        self.assertEqual(sub_trie.keys(), expected_keys)
        self.assertEqual(sub_trie.terminal_marker, trie.terminal_marker)


class TestMutableTree(TestTrie):
    def test_setitem(self):
        D_KEY = (2, 3, 4)
        D = "d"
        dct = {self.A_KEY: self.A, self.B_KEY: self.B, self.C_KEY: self.C}
        trie = MutableTrie.from_dict(self.TERM, dct)
        self.assertIsNone(trie.get(D_KEY, None))
        trie[D_KEY] = D
        self.assertEqual(D, trie[D_KEY])

    def test_delitem(self):
        dct = {
            self.A_KEY: self.A,
            self.B_KEY: self.B,
            self.C_KEY: self.C,
        }
        trie = MutableTrie.from_dict(self.TERM, dct)
        del trie[self.C_KEY]
        self.assertIsNone(trie.get(self.C_KEY, None))
