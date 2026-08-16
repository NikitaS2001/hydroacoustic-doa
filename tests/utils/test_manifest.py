"""Unit tests for utils.manifest."""

from __future__ import annotations

import numpy as np

from hydro_doa_mvp.utils.manifest import (
    build_eligibility_record,
    canonical_json_bytes,
    object_hash,
)


def test_canonical_json_stable_across_key_order():
    a = canonical_json_bytes({"b": 1, "a": "x"})
    b = canonical_json_bytes({"a": "x", "b": 1})
    assert a == b == b'{"a":"x","b":1}'
    assert object_hash({"b": 1, "a": "x"}) == object_hash({"a": "x", "b": 1})


def test_eligibility_ok_and_zero_power():
    rec = build_eligibility_record("primary-support-500-1400hz-v1", np.array([2.9e-4, 3.1e-4]))
    assert rec.eligible and rec.reason == "ok"
    assert len(rec.eligibility_hash) == 64
    rec_bad = build_eligibility_record("primary-support-500-1400hz-v1", np.array([2.9e-4, 0.0]))
    assert not rec_bad.eligible and rec_bad.reason == "zero_projected_power"
    rec_nan = build_eligibility_record("primary-support-500-1400hz-v1", np.array([np.nan, 1.0]))
    assert not rec_nan.eligible and rec_nan.reason == "non_finite_projected_power"
    # hash must change with content
    assert rec.eligibility_hash != rec_bad.eligibility_hash
