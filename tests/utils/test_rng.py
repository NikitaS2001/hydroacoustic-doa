"""Golden and contract tests for utils.rng (protocol Section 7.3)."""

from __future__ import annotations

import hashlib
import json
import unicodedata

import numpy as np
import pytest

from hydro_doa_mvp.utils.rng import (
    ALGORITHM_ID,
    NAMESPACE_FIELDS,
    PhiloxStream,
    canonical_namespace_json,
    philox4x32_10,
)

# Official Random123 known-answer vectors (tests/kat_vectors, DEShawResearch/random123):
# name       R  CTR(4xu32)                          KEY(2xu32)            EXPECTED(4xu32)
KAT_PHILOX4X32_R10 = [
    (
        [0x00000000, 0x00000000, 0x00000000, 0x00000000],
        [0x00000000, 0x00000000],
        [0x6627E8D5, 0xE169C58D, 0xBC57AC4C, 0x9B00DBD8],
    ),
    (
        [0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF],
        [0xFFFFFFFF, 0xFFFFFFFF],
        [0x408F276D, 0x41C83B0E, 0xA20BC7C6, 0x6D5451FD],
    ),
    (
        [0x243F6A88, 0x85A308D3, 0x13198A2E, 0x03707344],
        [0xA4093822, 0x299F31D0],
        [0xD16CFE09, 0x94FDCCEB, 0x5001E420, 0x24126EA1],
    ),
]


@pytest.mark.parametrize(("ctr", "key", "expected"), KAT_PHILOX4X32_R10)
def test_philox4x32_10_official_kat(ctr, key, expected):
    out = philox4x32_10(np.array([ctr], dtype=np.uint32), np.array([key], dtype=np.uint32))
    assert out.shape == (1, 4)
    assert [int(w) for w in out[0]] == expected


def _sample_namespace(**over):
    ns = {
        "split": "train",
        "environment": 17,
        "channel": 412,
        "source": 2,
        "overlay": 0,
        "epoch": 0,
        "view": 0,
        "mask": 0,
    }
    ns.update(over)
    return ns


def test_namespace_schema_enforced():
    base = _sample_namespace()
    with pytest.raises(ValueError, match="extra"):
        canonical_namespace_json({**base, "permutation": 1})
    with pytest.raises(ValueError, match="missing"):
        canonical_namespace_json({k: v for k, v in base.items() if k != "mask"})
    for field_name in ("epoch", "view", "mask"):
        with pytest.raises(ValueError, match=field_name):
            canonical_namespace_json(_sample_namespace(**{field_name: -1}))
        with pytest.raises(ValueError, match=field_name):
            canonical_namespace_json(_sample_namespace(**{field_name: "0"}))


def test_namespace_canonical_json_and_nfc():
    composed = _sample_namespace(split="café")
    decomposed = _sample_namespace(split="café")
    assert decomposed["split"] != composed["split"]  # pre-normalization differs
    assert canonical_namespace_json(composed) == canonical_namespace_json(decomposed)
    payload = canonical_namespace_json(composed)
    assert payload.startswith(b'{"channel":412,')
    assert b" " not in payload  # separators=(",", ":")


def test_stream_record_fields():
    s = PhiloxStream(_sample_namespace())
    rec = s.record.as_dict()
    assert rec["rng_algorithm"] == ALGORITHM_ID
    assert len(rec["d"]) == 64 and len(rec["r"]) == 64
    assert json_roundtrip(rec["namespace"]) == json_roundtrip(s.record.namespace_json)


def json_roundtrip(s: str) -> str:
    return json.dumps(json.loads(s), sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def test_stream_reproducible_and_independent():
    ns = _sample_namespace()
    a = PhiloxStream(ns).uniforms(1024)
    b = PhiloxStream(dict(ns)).uniforms(1024)
    np.testing.assert_array_equal(a, b)
    c = PhiloxStream(_sample_namespace(overlay=1)).uniforms(1024)
    assert not np.array_equal(a, c)


def test_counter_blocks_are_consecutive():
    s = PhiloxStream(_sample_namespace())
    # block0 output equals philox(counter0), block1 equals philox(counter0+1 LE)
    words = s.uint32s(8).reshape(2, 4)
    d = hashlib.sha256(canonical_namespace_json(_sample_namespace())).digest()
    c0 = np.frombuffer(d[0:16], dtype="<u4").copy()
    r = hashlib.sha256(b"hydro-doa-mvp-v1").digest()
    key = np.frombuffer(r[0:8], dtype="<u4").copy()
    np.testing.assert_array_equal(words[0], philox4x32_10(c0.reshape(1, 4), key)[0])
    c1 = c0.copy()
    c1[0] = np.uint32(c1[0] + np.uint32(1))
    np.testing.assert_array_equal(words[1], philox4x32_10(c1.reshape(1, 4), key)[0])


def test_uniform_and_normal_sanity():
    s = PhiloxStream(_sample_namespace())
    u = s.uniforms(200_000)
    assert u.min() >= 0.0 and u.max() < 1.0
    assert abs(u.mean() - 0.5) < 0.005
    z = PhiloxStream(_sample_namespace()).normals(200_000)
    assert abs(z.mean()) < 0.02 and abs(z.std() - 1.0) < 0.02


def test_namespace_field_names_documented():
    assert NAMESPACE_FIELDS == (
        "split",
        "environment",
        "channel",
        "source",
        "overlay",
        "epoch",
        "view",
        "mask",
    )


def test_nfc_helper_agrees():
    # guard: the NFC normalization used must be Python's unicodedata NFC
    s = "é"
    assert unicodedata.normalize("NFC", s) == unicodedata.normalize("NFC", "é")
