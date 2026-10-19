"""Reversible, canonical serialization for a bounded Phase 1C reader bundle.

All values are tagged so a dict with a tuple key or a string that resembles a
type tag is unambiguous. The digest detects accidental mutation; it is not a
cryptographic signature or a substitute for access control.
"""

from datetime import date, datetime, time
from decimal import Decimal
from hashlib import sha256
import json
from uuid import UUID


FORMAT_VERSION = 1


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def _encode(value):
    if value is None:
        return ["null"]
    if type(value) is bool:
        return ["bool", value]
    if type(value) is int:
        return ["int", str(value)]
    if type(value) is str:
        return ["str", value]
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise TypeError("Non-finite Decimal cannot be sealed")
        return ["decimal", str(value)]
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise TypeError("Naive datetime cannot be sealed")
        return ["datetime", value.isoformat()]
    if isinstance(value, date):
        return ["date", value.isoformat()]
    if isinstance(value, time):
        if value.tzinfo is not None and value.utcoffset() is None:
            raise TypeError("Ambiguous time zone cannot be sealed")
        return ["time", value.isoformat()]
    if isinstance(value, UUID):
        return ["uuid", str(value)]
    if type(value) is tuple:
        return ["tuple", [_encode(item) for item in value]]
    if type(value) is list:
        return ["list", [_encode(item) for item in value]]
    if type(value) is dict:
        entries = [(_encode(key), _encode(item)) for key, item in value.items()]
        entries.sort(key=lambda pair: _json(pair[0]))
        return ["dict", [[key, item] for key, item in entries]]
    raise TypeError(f"Unsupported evidence type: {type(value).__name__}")


def _decode(node):
    if not isinstance(node, list) or not node or not isinstance(node[0], str):
        raise ValueError("Invalid typed evidence node")
    tag = node[0]
    if tag == "null" and len(node) == 1:
        return None
    if len(node) != 2:
        raise ValueError("Invalid typed evidence payload")
    value = node[1]
    if tag == "bool" and type(value) is bool:
        return value
    if tag == "int" and isinstance(value, str):
        result = int(value)
        if str(result) == value:
            return result
    if tag == "str" and isinstance(value, str):
        return value
    if tag == "decimal" and isinstance(value, str):
        result = Decimal(value)
        if result.is_finite() and str(result) == value:
            return result
    if tag == "datetime" and isinstance(value, str):
        result = datetime.fromisoformat(value)
        if result.tzinfo is not None and result.utcoffset() is not None and result.isoformat() == value:
            return result
    if tag == "date" and isinstance(value, str):
        result = date.fromisoformat(value)
        if result.isoformat() == value:
            return result
    if tag == "time" and isinstance(value, str):
        result = time.fromisoformat(value)
        if result.isoformat() == value:
            return result
    if tag == "uuid" and isinstance(value, str):
        result = UUID(value)
        if str(result) == value:
            return result
    if tag in ("tuple", "list") and isinstance(value, list):
        items = [_decode(item) for item in value]
        return tuple(items) if tag == "tuple" else items
    if tag == "dict" and isinstance(value, list):
        result = {}
        for entry in value:
            if not isinstance(entry, list) or len(entry) != 2:
                raise ValueError("Invalid dictionary entry")
            key, item = _decode(entry[0]), _decode(entry[1])
            if key in result:
                raise ValueError("Duplicate decoded dictionary key")
            result[key] = item
        return result
    raise ValueError(f"Invalid or unsupported evidence tag: {tag}")


def seal(bundle: dict) -> tuple[str, str, int]:
    """Return canonical JSON, SHA-256, and UTF-8 byte size."""
    if type(bundle) is not dict:
        raise TypeError("Reader bundle must be a dict")
    raw = _json({"format_version": FORMAT_VERSION, "bundle": _encode(bundle)})
    encoded = raw.encode("utf-8")
    return raw, sha256(encoded).hexdigest(), len(encoded)


def unseal(serialized: str, expected_sha256: str) -> dict:
    encoded = serialized.encode("utf-8")
    if sha256(encoded).hexdigest() != expected_sha256:
        raise ValueError("Sealed evidence digest mismatch")
    payload = json.loads(serialized)
    if set(payload) != {"format_version", "bundle"} or payload["format_version"] != FORMAT_VERSION:
        raise ValueError("Unsupported sealed evidence format")
    result = _decode(payload["bundle"])
    if type(result) is not dict or seal(result)[0] != serialized:
        raise ValueError("Noncanonical or invalid reader bundle")
    return result
