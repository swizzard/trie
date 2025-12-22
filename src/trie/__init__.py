"""Trie implementation"""

from collections.abc import Iterable
from collections import defaultdict
from typing import Hashable, Self, TypeVar

__all__ = ["Trie", "MutableTrie", "StringTrie", "MutableStringTrie"]


NonTerminal = TypeVar("NonTerminal", bound=Hashable)
TerminalValue = TypeVar("Terminal")
R = TypeVar("R")


class HashableIterable[NonTerminal](Iterable[NonTerminal], Hashable):
    pass


class Trie[TerminalValue, NonTerminal]:
    """The Trie is generic in its leaves and in its branches.
    Branches are of type `NonTerminal`, leaves are of type `TerminalValue`
    "Keys" are `Iterable[NonTerminal]`.
    """

    # The final trie. We have to erase types to account for recursion
    children: dict

    # A value of type `NonTerminal` used to indicate a complete key sequence
    # IMPORTANT: Make sure this value never occurs in a key, or undesired
    # behavior will result
    terminal_marker: NonTerminal

    def __init__(self, terminal_marker, children):
        """Create a new `Trie`.
        NOTE: This expects `cls.finalize` to have already been called on
        `children`. Use `cls.from_dict` or `cls.from_items` instead.
        """
        self.children = children
        self.terminal_marker = terminal_marker

    @classmethod
    def from_dict(
        cls,
        terminal_marker: NonTerminal,
        dct: dict[HashableIterable[NonTerminal], TerminalValue],
    ):
        """Create a Trie from a dictionary.
        Keys are decomposed and the values stored at `terminal_marker` in the
        lowest-level corresponding sub-trie.

        If `terminal_marker == 0`,
        then `{(1, 2, 3, 4): "foo"}` -> `{1: {2: {3: {4: {0: "foo"}}}}}`
        """
        return cls.from_items(terminal_marker, dct.items())

    @classmethod
    def from_items(
        cls,
        terminal_marker: NonTerminal,
        items: Iterable[(Iterable[NonTerminal], TerminalValue)],
    ):
        """Create a Trie from an iterable of `(key, value)` tuples.
        Keys are decomposed and the values stored at `terminal_marker` in the
        lowest-level corresponding sub-trie.

        If `terminal_marker == 0`,
        then `([1, 2, 3, 4], "foo")` -> `{1: {2: {3: {4: {0: "foo"}}}}}`
        """
        children = cls.make_children()
        for key, terminal in items:
            level = cls.iter_key(children, key)
            level[terminal_marker] = terminal
        frozen = cls.finalize(children)
        return cls(terminal_marker, frozen)

    def get(self, key: Iterable[NonTerminal], default: R) -> TerminalValue | R:
        """Retrieve a value from the trie, or `default` if the (entire) `key`
        isn't found
        """
        return self._subtrie(key).get(self.terminal_marker, default)

    def __getitem__(self, key: Iterable[NonTerminal]) -> TerminalValue:
        """Retrieve a value from the trie, raising a `KeyError` if the (entire)
        `key` isn't found
        """
        try:
            return self._subtrie(key)[self.terminal_marker]
        except KeyError:
            raise KeyError(key)

    def get_subtrie(self, key: Iterable[NonTerminal]) -> Self:
        """Get a new Trie corresponding to the subtrie at `key`
        NB: unlike `get` and `__getitem__`, this method does not append
        `terminal_value` to `key`
        """
        return Trie(self.terminal_marker, self._subtrie(key))

    def keys(self):
        """The 0th element of every key in the Trie"""
        return self.children.keys()

    def items(self):
        """`(E, T)` tuples, where `E` is the 0th element of a key and `T`
        is the corresponding subtrie
        """
        for k, v in self.children.items():
            yield (k, Trie(self.terminal_marker, v))

    def __contains__(self, item: Iterable[NonTerminal]) -> bool:
        return bool(self.get(item, False))

    def _subtrie(self, key: Iterable[NonTerminal]) -> dict:
        return self.iter_key(self.children, key)

    @classmethod
    def finalize(cls, children: defaultdict):
        """Finalize `children` by recursively casting to `dict`"""
        d = {}
        for k, v in children.items():
            if isinstance(v, defaultdict):
                d[k] = cls.finalize(v)
            else:
                d[k] = v
        return d

    @classmethod
    def make_children(cls) -> defaultdict:
        """Helper to generate recursive `defaultdict`s.
        Stolen from https://stackoverflow.com/a/19189356
        """
        return defaultdict(cls.make_children)

    @staticmethod
    def iter_key(children: dict, key: Iterable[NonTerminal]) -> TerminalValue | dict:
        [fst, *rest] = key
        curr_level = children
        while len(rest) > 0:
            old_level = curr_level
            curr_level = old_level[fst]
            [fst, *rest] = rest
        return curr_level[fst]

    def _prefixes(self, k: Iterable[NonTerminal]) -> Iterable[Iterable[NonTerminal]]:
        yield k
        for key, value in self._subtrie(k).items():
            if key == self.terminal_marker:
                continue
            k2 = k + key
            yield from self._prefixes(k2)

    def prefixes(self) -> Iterable[Iterable[NonTerminal]]:
        for key in self.keys():
            yield from self._prefixes(key)

    def prefixes_from(
        self, key: Iterable[NonTerminal]
    ) -> Iterable[Iterable[NonTerminal]]:
        gen = self._prefixes(key)
        next(gen)  # skip `key`
        yield from gen


class MutableTrie(Trie[TerminalValue, NonTerminal]):
    """A `Trie` that can be modified after creation."""

    # Left as `defaultdict` for easier insertion
    children: defaultdict

    def __getitem__(self, key: Iterable[NonTerminal]) -> TerminalValue:
        # `defaultdict.__getitem__` doesn't behave like we want
        value = self._subtrie(key).get(self.terminal_marker, None)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: Iterable[NonTerminal], value: TerminalValue):
        level = self.iter_key(self.children, key)
        level[self.terminal_marker] = value

    def __delitem__(self, key: Iterable[NonTerminal]):
        level = self.iter_key(self.children, key)
        del level[self.terminal_marker]

    @classmethod
    def finalize(cls, children: defaultdict):
        """Leave `children` as a `defaultdict`"""
        return children


class StringTrie(Trie[TerminalValue, str]):
    """A `Trie` whose keys are strings and whose `terminal_marker` is always
    the empty string.
    """

    # Always the empty string
    terminal_marker: str

    def __init__(self, children):
        super().__init__("", children)

    @classmethod
    def from_dict(cls, dct: dict[str, TerminalValue]):
        # `terminal_marker` is always the empty string
        return cls.from_items(dct.items())

    @classmethod
    def from_items(cls, items: Iterable[(str, TerminalValue)]):
        # `terminal_marker` is always the empty string
        children = cls.make_children()
        for key, terminal in items:
            level = cls.iter_key(children, key)
            level[""] = terminal
        frozen = cls.finalize(children)
        return cls(frozen)


class MutableStringTrie(StringTrie[TerminalValue], MutableTrie[TerminalValue, str]):
    """A string-keyed `Trie` that supports post-creation mutability."""

    def __init__(self, children):
        super(StringTrie).__init__(children)


class TrieSet(Trie[bool, NonTerminal]):
    def __init__(self, terminal_marker, children):
        super().__init__(terminal_marker, children)

    @classmethod
    def from_keys(
        cls, terminal_marker: NonTerminal, keys: Iterable[Iterable[NonTerminal]]
    ) -> Self:
        return cls.from_items((k, True) for k in keys)

    def is_prefix(self, k: Iterable[NonTerminal]):
        try:
            self._subtrie(k)
            return True
        except KeyError:
            return False
