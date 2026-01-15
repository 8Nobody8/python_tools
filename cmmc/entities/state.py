"""
State

A lightweight mutable key-value store that behaves like a dictionary
but also allows attribute-style access (e.g. state.foo as well as state['foo']).

Originally developed for DSPy-based pipeline orchestration, where modules
read and write shared named variables (inputs/outputs) across a structured program.

Features:

Dot and bracket access

Clean dict-like API (get, items, values, etc.)

Safe internal storage with _data

Easy equality and serialization

Can be reused in any project that needs a flexible, introspectable state container.

"""

from collections.abc import MutableMapping


class State(MutableMapping):
    """
    A hybrid object-dict state container.

    This is a convenience wrapper that allows both dot-access (`state.foo`) and
    dict-style access (`state['foo']`) to the same underlying key-value store.
    """

    def __init__(self, initial=None):
        object.__setattr__(self, "_data", dict(initial) if initial else {})

    def __contains__(self, key):
        return key in self._data

    def __delitem__(self, key):
        del self._data[key]

    def __eq__(self, other):
        if isinstance(other, State):
            return self._data == other._data
        elif isinstance(other, dict):
            return self._data == other
        return NotImplemented

    def __getattr__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(f"'State' object has no attribute '{key}'")

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"State({self._data!r})"

    def __setattr__(self, key, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            self._data[key] = value

    def __setitem__(self, key, value):
        self._data[key] = value

    def as_dict(self):
        return self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()
