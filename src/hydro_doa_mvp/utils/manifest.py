"""Manifest hashing and record schemas (protocol Sections 7.3, 7.2a, 15).

Manifest rows serialize with the same canonical JSON rules as RNG namespaces:
UTF-8, ``sort_keys=True``, ``ensure_ascii=False``, ``separators=(",", ":")``.
Content hashes are SHA-256 over canonical bytes or raw file bytes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def object_hash(obj: Any) -> str:
    """SHA-256 over the canonical JSON serialization of ``obj``."""
    return sha256_hex(canonical_json_bytes(obj))


@dataclass(frozen=True)
class EligibilityRecord:
    """Primary DOA eligibility of one clean source realization (Section 7.2a)."""

    profile_id: str
    per_sensor_projected_power: tuple[float, ...]
    array_mean_power: float
    eligible: bool
    reason: str

    @property
    def eligibility_hash(self) -> str:
        payload = {
            "profile_id": self.profile_id,
            "per_sensor_projected_power": list(self.per_sensor_projected_power),
            "array_mean_power": self.array_mean_power,
            "eligible": self.eligible,
            "reason": self.reason,
        }
        return object_hash(payload)


def build_eligibility_record(
    profile_id: str,
    per_sensor_projected_power: np.ndarray,
) -> EligibilityRecord:
    """Exact domain check: finite and strictly positive at every active sensor."""
    p = np.asarray(per_sensor_projected_power, dtype=float)
    all_finite = bool(np.all(np.isfinite(p)))
    all_positive = bool(np.all(p > 0.0))
    eligible = all_finite and all_positive
    if eligible:
        reason = "ok"
    elif not all_finite:
        reason = "non_finite_projected_power"
    else:
        reason = "zero_projected_power"
    return EligibilityRecord(
        profile_id=profile_id,
        per_sensor_projected_power=tuple(float(x) for x in p),
        array_mean_power=float(p.mean()) if p.size else float("nan"),
        eligible=eligible,
        reason=reason,
    )


@dataclass(frozen=True)
class ViewIdentity:
    """Child inference-view identity fields (Section 7.2a)."""

    inference_view_id: str
    lower_edge_hz: float
    upper_edge_hz: float
    upper_edge_included: bool
    sample_rate_hz: int
    sample_count: int
    retained_bin_mask_hash: str
    scalar_a_v: float
    target_snr_db_view: float
    achieved_snr_db_view: float
    parent_derived_row_hash: str = ""
    dft_convention: str = "real-dft-orthogonal-none-v1"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DerivedRowIdentity:
    """Replay-key fields of one derived example row (Section 7.3)."""

    base_channel_hash: str
    channel_config: dict[str, Any]
    source_waveform_id: str
    source_waveform_parameters: dict[str, Any]
    noise_class: str
    interference_class: str
    base_target_snr_db: float
    base_applied_scalar: float
    overlay_version: str
    generator_version: str
    rng: dict[str, str]
    eligibility: dict[str, Any]
    views: tuple[ViewIdentity, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["views"] = [v.as_dict() for v in self.views]
        return d

    @property
    def row_hash(self) -> str:
        return object_hash(self.as_dict())
