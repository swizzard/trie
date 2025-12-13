# Trie

## Introduction

This library provides `Trie`s (prefix trees). These tries operate similarly
to regular `dict`s, except keys are decomposed and values stored under a
special leaf value.

Note: When initializing a `Trie`, it's important that the value chosen for
`terminal_marker` _does not appear_ in valid keys, or else undesirable
behavior will result.

## Usage

### `Trie`

The functionality of `Trie`, the base class, is shared by its subclasses. 

```python
>>> items = [[1, 2, 3]: "A", [1, 2, 4]: "B", [2, 3, 4, 5]: "C"]
# use from_items when key sequences aren't hashable
>>> trie = Trie.from_items(0, items)  # Trie[int, str]
# or
>>> dct = {(1, 2, 3): 'A', (1, 2, 4): 'B', (2, 3, 4, 5): 'C'}
>>> trie = Trie.from_dict(0, dct)  # Trie[int, str]
# get
>>> trie[(1, 2, 4)] # "B"
# invalid key
>>> trie.get((1, 2, 5), "X") # "X"
# incomplete keys don't count
>>> trie.get((1, 2), "X")  # "X"
# but you can retrieve a subtrie
>>> sub = trie.get_subtrie((1, 2))
>>> sub.get([4], "X")  # "B"
# keys() and items() return "top-level" only
>>> list(trie.keys())  # [1, 2]
>>> list(trie.items()) # [(1, <Trie object at ...>), (2, <Trie object at ...>)]
>>> list(sub.keys()) # [3, 4]
# __contains__() checks whole keys
>>> (1, 2, 3) in trie  # True
>>> (1, 2) in trie # False
```

### `MutableTrie`

`MutableTrie` adds `__setitem__` and `__delitem__` methods, permitting
post-creation mutation.

```python
>>> dct = {(1, 2, 3): 'A', (1, 2, 4): 'B', (2, 3, 4, 5): 'C'}
>>> trie = MutableTrie.from_dict(0, dct)  # MutableTrie[int, str]
>>> trie[(4, 5, 6)] = 'N'
>>> trie[(4, 5, 6)]  # 'N'
>>> del trie[(1, 2, 3)]
>>> trie.get((1, 2, 3), 'X')  # 'X'
```

### `StringTrie` and `MutableStringTrie`

`StringTrie` is a `Trie` specialized for `str`-typed keys, with `""` (the
empty string) used as the `terminal_value`. `MutableStringTrie` is a
`StringTrie` that permits post-creation mutability.

```python
>>> dct = {"ace": 1, "act": 2, "cab": 3}
# terminal_marker not required in from_dict / from_items
>>> trie = StringTrie.from_dict(dct)  # StringTrie[int]
```
