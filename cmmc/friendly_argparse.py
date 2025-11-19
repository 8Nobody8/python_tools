import argparse
from collections.abc import Mapping
from typing import Any, Dict, List, Sequence, Tuple, Union, Optional


def _to_bool(val: Any) -> bool:
    bool_true = {"1", "true", "yes", "y", "on"}
    bool_false = {"0", "false", "no", "n", "off"}
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.strip().lower()
        if v in bool_true:
            return True
        if v in bool_false:
            return False
    if isinstance(val, int) or isinstance(val, float):
        if val == 1:
            return True
        if val == 0:
            return False
    raise ValueError(f"Cannot interpret {val!r} as boolean")


def _to_type(val: Any):
    if not isinstance(val, str):
        return val
    mapping = {
        "str": str,
        "string": str,
        "int": int,
        "integer": int,
        "float": float,
        "bool": bool,
        "boolean": bool,
    }
    key = val.lower()
    if key in mapping:
        return mapping[key]
    raise ValueError(f"Unknown type string {val!r}")


class Arg(Mapping):
    """
    Read-only mapping that also supports attribute access:

        args["input"]
        args.input

    Use dict(args) if you want a plain dict copy.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = dict(data)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __repr__(self) -> str:
        return f"Arg({self._data!r})"

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


class ArgHelper:
    """
    Singleton-style wrapper around argparse.ArgumentParser.

    - add_arg(*args, **kwargs)    → define one arg
    - add_from_spec(spec)         → define one arg from a 'spec' object
    - delete_arg(name)            → delete a single argument
    - reset()                     → wipe parser and definitions
    - parse()                     → parse sys.argv into an Arg
    """

    def __init__(self, description: Optional[str] = None) -> None:
        self.parser = argparse.ArgumentParser(description=description)
        # dest name -> (flags, kwargs)
        self.defined: Dict[str, Tuple[List[str], Dict[str, Any]]] = {}

    def _infer_dest_from_flags(self, flags: Sequence[str]) -> str:
        long_flags = [f for f in flags if f.startswith("--")]
        if long_flags:
            base = long_flags[0][2:]
        else:
            base = flags[0].lstrip("-")
        return base.replace("-", "_")

    def _normalise(
        self, args: Sequence[Any], kwargs: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Any], str]:
        kwargs = dict(kwargs)  # shallow copy
        flags: List[str] = []

        # Case 1: argparse-style positional/option flags were given
        if args:
            flags = [str(a) for a in args]
            dest = kwargs.get("dest") or self._infer_dest_from_flags(flags)

        else:
            # Case 2: "friendly" dict interface with keys like name, shortform, flag
            name = kwargs.pop("name", None)
            if not name:
                raise ValueError(
                    "Argument specification must include 'name' when no positional flags are given"
                )
            name_str = str(name)

            shortform = kwargs.pop("shortform", None)
            flag = kwargs.pop("flag", True)
            if isinstance(flag, str):
                flag = _to_bool(flag)

            if flag:
                # optional arg with dashes
                if shortform:
                    s = str(shortform)
                    if len(s) != 1:
                        raise ValueError(
                            f"shortform must be a single character, got {shortform!r}"
                        )
                    flags.append(f"-{s}")
                long_flag = "--" + name_str.replace("_", "-")
                flags.append(long_flag)
            else:
                # positional arg
                flags.append(name_str)

            kwargs.setdefault("dest", name_str)
            dest = kwargs["dest"]

        if "type" in kwargs:
            kwargs["type"] = _to_type(kwargs["type"])

        if "required" in kwargs and isinstance(kwargs["required"], str):
            kwargs["required"] = _to_bool(kwargs["required"])

        return flags, kwargs, dest

    def add_arg(self, *args: Any, **kwargs: Any) -> str:
        """
        Define a single argument.

        Usage patterns:
        - add_arg("input_file")                           # positional
        - add_arg("-i", "--input-file", type=str)         # argparse style
        - add_arg(name="input", type="str", required="1") # friendly dict style
        """
        flags, final_kwargs, dest = self._normalise(args, kwargs)

        if dest in self.defined:
            print(
                f"[arghelper] Warning: argument {dest!r} already defined, "
                f"overriding previous definition"
            )

        self.defined[dest] = (flags, final_kwargs)
        self.parser.add_argument(*flags, **final_kwargs)
        return dest

    def add_from_spec(
        self, spec: Union[Dict[str, Any], Tuple[Sequence[Any], Dict[str, Any]]]
    ) -> str:
        """
        Accept either:
        - dict, e.g. {"name": "input", "type": "str", "required": "True", ...}
        - (args_sequence, kwargs_dict), mimicking add_argument signature
        """
        if isinstance(spec, dict):
            return self.add_arg(**spec)
        if (
            isinstance(spec, (list, tuple))
            and len(spec) == 2
            and isinstance(spec[1], dict)
        ):
            positional, kw = spec
            return self.add_arg(*positional, **kw)
        raise TypeError("Spec must be a dict or (args_sequence, kwargs_dict)")

    def delete_arg(self, name: str) -> bool:
        """
        Delete a single argument by its logical name/dest.

        Returns True if something was deleted, False otherwise.
        """
        dest = name
        if dest not in self.defined:
            return False

        flags, _ = self.defined.pop(dest)

        # Remove associated action(s) from the parser internals
        to_remove = []
        for action in list(self.parser._actions):  # type: ignore[attr-defined]
            if action.dest == dest or any(
                f in getattr(action, "option_strings", []) for f in flags
            ):
                to_remove.append(action)

        for action in to_remove:
            # remove from main actions list
            self.parser._actions.remove(action)  # type: ignore[attr-defined]

            # remove from action groups
            for group in self.parser._action_groups:  # type: ignore[attr-defined]
                if action in group._group_actions:  # type: ignore[attr-defined]
                    group._group_actions.remove(action)

            # remove from option_string_actions mapping
            for opt in getattr(action, "option_strings", []):
                self.parser._option_string_actions.pop(opt, None)  # type: ignore[attr-defined]

        return True

    def reset(self, description: Optional[str] = None) -> None:
        """
        Reset the underlying ArgumentParser and all definitions.
        """
        self.parser = argparse.ArgumentParser(description=description)
        self.defined.clear()

    def parse(self) -> Arg:
        """
        Call parser.parse_args() and return an Arg (dict-like + attrs).
        """
        ns = self.parser.parse_args()
        data = vars(ns)
        return Arg(data)


_helper: Optional[ArgHelper] = None


def _get_helper(description: Optional[str] = None) -> ArgHelper:
    global _helper
    if _helper is None:
        _helper = ArgHelper(description=description)
    elif description is not None and _helper.parser.description is None:
        _helper.parser.description = description
    return _helper


def def_arg(*args: Any, **kwargs: Any) -> str:
    """
    Define a single argument.
    Can be called multiple times, even before get_args().
    """
    helper = _get_helper()
    return helper.add_arg(*args, **kwargs)


def def_args(*specs):
    helper = _get_helper()
    return [helper.add_from_spec(spec) for spec in specs]


def get_args(*specs: Any, description: Optional[str] = None) -> Arg:
    """
    Optionally define more args, then parse and return an Arg.

    - If called with specs, those specs are turned into arguments.
    - If called with no specs, it parses whatever has already been defined
      via def_arg(...) or previous get_args(...) calls.
    """
    helper = _get_helper(description=description)
    for spec in specs:
        helper.add_from_spec(spec)
    return helper.parse()


def delete_arg(name: str) -> bool:
    """
    Delete a single argument by its logical name/dest.
    """
    helper = _get_helper()
    return helper.delete_arg(name)


def delete_args(*names: str) -> Dict[str, bool]:
    """
    Delete multiple arguments. Returns a mapping name -> deleted_flag.
    """
    helper = _get_helper()
    return {name: helper.delete_arg(name) for name in names}


def reset_args(description: Optional[str] = None) -> None:
    """
    Delete all arguments and reset the parser.
    """
    helper = _get_helper()
    helper.reset(description=description)
