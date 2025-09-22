#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Union, Final, cast

JSONScalar = str
JSONMap = Dict[str, Any]
JSONList = List[Any]
InnerDict = Dict[str, str]
TopLevelValue = Union[InnerDict, List[InnerDict]]
TopLevel = Dict[str, TopLevelValue]

_SEPARATORS: Final = (",", ":")


def _normalize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _normalize(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        norm = [_normalize(e) for e in obj]
        norm.sort(key=lambda e: json.dumps(e, sort_keys=True, separators=_SEPARATORS))
        return norm
    if isinstance(obj, str):
        return obj
    raise TypeError(f"Unsupported type: {type(obj).__name__}")


def hash_structure(data: TopLevel) -> str:
    norm = _normalize(data)
    payload = json.dumps(norm, sort_keys=True, separators=_SEPARATORS)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _demo() -> None:
    a: TopLevel = {
        "users": [
            {"id": "2", "name": "Bob"},
            {"id": "1", "name": "Alice"},
        ],
        "config": {"level": "5", "mode": "debug"},
    }
    b: TopLevel = {
        "config": {"mode": "debug", "level": "5"},
        "users": [
            {"name": "Alice", "id": "1"},
            {"name": "Bob", "id": "2"},
        ],
    }
    c: TopLevel = {
        "config": {"mode": "debug", "level": "5"},
        "users": [
            {"name": "Bob", "id": "2"},
            {"name": "Alice", "id": "1"},
            {"extra": "ignored?"},  # only to show a structural change
        ],
    }

    print("hash(a):", hash_structure(a))
    print("hash(b):", hash_structure(b))
    print("hash(c):", hash_structure(c))
    print("a == b (by hash):", hash_structure(a) == hash_structure(b))
    print("a == c (by hash):", hash_structure(a) == hash_structure(c))


if __name__ == "__main__":
    _demo()
