"""Focused tests for `scripts/eval_kizomba_beats.py` metric math."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "eval_kizomba_beats.py"

spec = importlib.util.spec_from_file_location("eval_kizomba_beats", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules["eval_kizomba_beats"] = mod
spec.loader.exec_module(mod)


def test_nearest_dist_basic():
    times = np.array([0.0, 0.5, 1.05])
    refs = np.array([0.0, 1.0, 2.0])
    d = mod._nearest_dist(times, refs)
    np.testing.assert_allclose(d, [0.0, 0.5, 0.05])


def test_nearest_dist_empty_inputs():
    assert mod._nearest_dist(np.array([]), np.array([1.0])).size == 0
    assert mod._nearest_dist(np.array([1.0]), np.array([])).size == 0


def test_nearest_dist_single_ref():
    d = mod._nearest_dist(np.array([0.0, 2.0]), np.array([1.0]))
    np.testing.assert_allclose(d, [1.0, 1.0])


def test_configs_registry_has_current_mirror():
    """The 'current' config must mirror production constants exactly so
    `--sweep` includes the live baseline."""
    from rytmi import dsp

    cfg = mod.CONFIGS["current"]
    assert cfg.band == ("low", dsp._KIZOMBA_BATIDA_LPF_HZ)
    assert cfg.wait_ms == dsp._KIZOMBA_BATIDA_WAIT_MS
    assert cfg.delta_pct == dsp._KIZOMBA_BATIDA_DELTA_PCT


def test_compute_beats_runs_on_synthetic():
    """`compute_beats` must accept every band kind and return finite times."""
    from rytmi.types import AudioData

    sr = 22050
    # 4 s of clicks every 0.6 s with low-frequency content.
    t = np.arange(int(4 * sr)) / sr
    sig = np.sin(2 * np.pi * 80.0 * t).astype(np.float32) * 0.05
    for k in range(7):
        i = int(k * 0.6 * sr)
        sig[i : i + 50] += 0.8
    audio = AudioData(samples=sig, sr=sr, duration=sig.size / sr)

    for name in ("current", "low_b8", "low_no_bt", "mid", "high", "multiband_sum"):
        beats = mod.compute_beats(audio, mod.CONFIGS[name])
        assert isinstance(beats, np.ndarray)
        assert np.all(np.isfinite(beats))
        # At least one beat picked on a 4 s click train.
        assert beats.size >= 1, f"{name} found no beats"
