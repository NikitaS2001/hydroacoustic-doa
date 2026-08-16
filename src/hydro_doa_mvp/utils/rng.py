"""Canonical RNG per the BELLHOP MVP protocol, Section 7.3.

All stochastic generation uses Random123 Philox4x32-10 keyed by a canonical
namespace-derived counter/key:

    D       = SHA-256(canonical_json_bytes(namespace))
    R       = SHA-256(b"hydro-doa-mvp-v1")
    counter = four little-endian uint32 words from D[0:16]
    key     = two little-endian uint32 words from R[0:8]

Subsequent blocks increment the 128-bit counter modulo 2**128 in little-endian
word order. The namespace schema is exactly
``split, environment, channel, source, overlay, epoch, view, mask``
(missing or additional fields are rejected); every string value is Unicode
NFC-normalized; ``epoch``, ``view`` and ``mask`` must be nonnegative integers;
the namespace serializes to UTF-8 JSON with ``sort_keys=True``,
``ensure_ascii=False`` and ``separators=(",", ":")``.

The Philox4x32-10 core is validated against the official Random123
known-answer vectors (tests/utils/test_rng.py).
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass

import numpy as np

NAMESPACE_FIELDS = ("split", "environment", "channel", "source", "overlay", "epoch", "view", "mask")
ALGORITHM_ID = "random123-philox4x32-10-v1"
R_DOMAIN = b"hydro-doa-mvp-v1"

_PHILOX_M0 = np.uint32(0xD2511F53)
_PHILOX_M1 = np.uint32(0xCD9E8D57)
_PHILOX_W0 = np.uint32(0x9E3779B9)
_PHILOX_W1 = np.uint32(0xBB67AE85)
_ROUNDS = 10


def philox4x32_10(counter: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Philox4x32 with 10 rounds (Random123 semantics).

    counter: uint32 array, last axis has 4 words (LE word order).
    key:     uint32 array, last axis has 2 words.
    Returns uint32 array with the same leading shape, 4 words on the last axis.

    Reference: Salmon et al., "Parallel Random Numbers: As Easy as 1, 2, 3",
    SC '11; implementation follows Random123 philox.h round/bumpkey order
    (round first with the original key, bump between rounds).
    """
    ctr = np.asarray(counter, dtype=np.uint32).reshape(-1, 4)
    k0 = np.uint32(np.asarray(key, dtype=np.uint32).reshape(-1, 2)[0, 0])
    k1 = np.uint32(np.asarray(key, dtype=np.uint32).reshape(-1, 2)[0, 1])
    with np.errstate(over="ignore"):  # uint32 wraparound is part of Philox
        for r in range(_ROUNDS):
            if r > 0:
                k0 = np.uint32(k0 + _PHILOX_W0)
                k1 = np.uint32(k1 + _PHILOX_W1)
            p0 = ctr[:, 0].astype(np.uint64)
            p2 = ctr[:, 2].astype(np.uint64)
            lo0 = (p0 * np.uint64(_PHILOX_M0)).astype(np.uint32)
            hi0 = ((p0 * np.uint64(_PHILOX_M0)) >> np.uint64(32)).astype(np.uint32)
            lo1 = (p2 * np.uint64(_PHILOX_M1)).astype(np.uint32)
            hi1 = ((p2 * np.uint64(_PHILOX_M1)) >> np.uint64(32)).astype(np.uint32)
            ctr = np.stack(
                [hi1 ^ ctr[:, 1] ^ k0, lo1, hi0 ^ ctr[:, 3] ^ k1, lo0], axis=-1
            ).astype(np.uint32)
    return ctr.reshape(np.shape(counter)[:-1] + (4,))


def canonical_namespace_json(namespace: dict) -> bytes:
    """Validate and serialize a namespace per protocol Section 7.3."""
    if set(namespace) != set(NAMESPACE_FIELDS):
        missing = sorted(set(NAMESPACE_FIELDS) - set(namespace))
        extra = sorted(set(namespace) - set(NAMESPACE_FIELDS))
        raise ValueError(f"bad namespace fields (missing={missing}, extra={extra})")
    normalized: dict[str, object] = {}
    for name in NAMESPACE_FIELDS:
        value = namespace[name]
        if name in ("epoch", "view", "mask"):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer, got {value!r}")
            normalized[name] = value
        elif isinstance(value, str):
            normalized[name] = unicodedata.normalize("NFC", value)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            normalized[name] = value
        else:
            raise ValueError(f"{name} must be str or number, got {type(value).__name__}")
    return json.dumps(
        normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


@dataclass(frozen=True)
class RngRecord:
    """Manifest record of one derived stream (protocol Section 7.3 replay key)."""

    namespace_json: str
    d_hex: str
    r_hex: str
    algorithm: str

    def as_dict(self) -> dict[str, str]:
        return {
            "namespace": self.namespace_json,
            "d": self.d_hex,
            "r": self.r_hex,
            "rng_algorithm": self.algorithm,
        }


class PhiloxStream:
    """A deterministic Philox4x32-10 stream derived from one namespace."""

    def __init__(self, namespace: dict) -> None:
        payload = canonical_namespace_json(namespace)
        d = hashlib.sha256(payload).digest()
        r = hashlib.sha256(R_DOMAIN).digest()
        self._counter0 = np.frombuffer(d[0:16], dtype="<u4").copy()
        self._key = np.frombuffer(r[0:8], dtype="<u4").copy()
        self.record = RngRecord(
            namespace_json=payload.decode("utf-8"),
            d_hex=d.hex(),
            r_hex=r.hex(),
            algorithm=ALGORITHM_ID,
        )

    def _blocks(self, n_words: int) -> np.ndarray:
        n_blocks = (n_words + 3) // 4
        counters = np.tile(self._counter0.astype(np.uint64), (n_blocks, 1))
        increments = np.arange(n_blocks, dtype=np.uint64)
        counters[:, 0] += increments & np.uint64(0xFFFFFFFF)
        carry = increments >> np.uint64(32)
        counters[:, 1] += carry & np.uint64(0xFFFFFFFF)
        carry2 = carry >> np.uint64(32)
        counters[:, 2] += carry2 & np.uint64(0xFFFFFFFF)
        counters[:, 3] += carry2 >> np.uint64(32)
        out = philox4x32_10(counters.astype(np.uint32), self._key)
        return out.reshape(-1)[:n_words]

    def uint32s(self, n: int) -> np.ndarray:
        """n uniform uint32 words from consecutive counter blocks."""
        if n < 0:
            raise ValueError("n must be nonnegative")
        return self._blocks(n)

    def uniforms(self, n: int) -> np.ndarray:
        """n uniform floats in [0, 1) with 32-bit resolution."""
        return self.uint32s(n).astype(np.float64) / float(2**32)

    def normals(self, n: int) -> np.ndarray:
        """n standard-normal floats via Box-Muller on uniform pairs."""
        m = n + (n & 1)
        u = self.uniforms(m).reshape(-1, 2)
        u = np.maximum(u, np.finfo(np.float64).tiny)
        r = np.sqrt(-2.0 * np.log(u[:, 0]))
        theta = 2.0 * np.pi * u[:, 1]
        return np.concatenate([r * np.cos(theta), r * np.sin(theta)])[:n]
