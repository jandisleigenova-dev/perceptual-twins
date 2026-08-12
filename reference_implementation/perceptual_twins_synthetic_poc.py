#!/usr/bin/env python3
"""Minimal synthetic estimand-recovery study for the Perceptual Twins design.

The implementation is deliberately small. It tests whether three paired causal
contrasts and one implementation-equivalence diagnostic are recoverable in a
resettable one-step microenvironment. It does not validate the full benchmark
or establish epistemic autonomy.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


CONDITIONS = ("A", "B_E", "C_E", "D", "E")
CONTRASTS = {
    "tau_tag": ("C_E", "B_E"),
    "tau_select": ("A", "E"),
    "tau_couple": ("E", "D"),
    "delta_exec_eq": ("E", "C_E"),
}


@dataclass(frozen=True)
class StudyConfig:
    seed: int = 20260805
    n_finite: int = 600
    n_reference: int = 20_000
    n_bootstrap: int = 1_000
    revision_steps: int = 12
    fault_steps: int = 10
    revision_noise: float = 0.10
    fault_hit: float = 0.80
    fault_false_alarm: float = 0.20
    prior_new_rule: float = 0.10


def entropy(prob: np.ndarray) -> float:
    p = np.clip(prob, 1e-15, 1.0)
    return float(-np.sum(p * np.log(p)))


def posterior_binary(prior_h1: float, like_h0: float, like_h1: float) -> float:
    num = prior_h1 * like_h1
    den = num + (1.0 - prior_h1) * like_h0
    return float(num / den) if den > 0 else prior_h1


def balanced_binary(rng: np.random.Generator, n: int) -> np.ndarray:
    values = np.array([0] * (n // 2) + [1] * (n - n // 2), dtype=int)
    rng.shuffle(values)
    return values


def balanced_multiclass(rng: np.random.Generator, n: int, k: int) -> np.ndarray:
    values = np.arange(n, dtype=int) % k
    rng.shuffle(values)
    return values


def restricted_permutation(
    rng: np.random.Generator,
    commands: np.ndarray,
    max_match_rate: float,
    attempts: int = 2_000,
) -> np.ndarray:
    """Permute commands while preserving exact marginals and limiting matches."""
    best = commands.copy()
    best_rate = 1.0
    for _ in range(attempts):
        candidate = rng.permutation(commands)
        rate = float(np.mean(candidate == commands))
        if rate < best_rate:
            best, best_rate = candidate, rate
        if rate <= max_match_rate:
            return candidate
    return best


def revision_likelihood(y: int, x: int, context: int, action: int, h: int, noise: float) -> float:
    if action == 0:
        return 0.5
    causal_class = x if h == 0 else (x ^ context)
    p_one = (1.0 - noise) if causal_class == 1 else noise
    return p_one if y == 1 else (1.0 - p_one)


def simulate_revision_anchor(rng: np.random.Generator, cfg: StudyConfig) -> dict[str, float]:
    n = cfg.revision_steps
    context = balanced_binary(rng, n)
    x = balanced_binary(rng, n)
    command_e = balanced_binary(rng, n)
    action_a = context.copy()
    action_d = restricted_permutation(rng, command_e, max_match_rate=0.25)
    u = rng.random(n)

    def generate(executed: np.ndarray) -> np.ndarray:
        p = np.empty(n, dtype=float)
        for t in range(n):
            if executed[t] == 0:
                p[t] = 0.5
            else:
                causal_class = x[t] ^ context[t]
                p[t] = (1.0 - cfg.revision_noise) if causal_class else cfg.revision_noise
        return (u < p).astype(int)

    y_a = generate(action_a)
    y_e = generate(command_e)
    y_d = generate(action_d)

    def learn(y: np.ndarray, observed_action: np.ndarray | None, integrate_action: bool) -> float:
        p_h1 = cfg.prior_new_rule
        area = 0.0
        for t in range(n):
            if integrate_action:
                l0 = 0.5 * revision_likelihood(y[t], x[t], context[t], 0, 0, cfg.revision_noise)
                l0 += 0.5 * revision_likelihood(y[t], x[t], context[t], 1, 0, cfg.revision_noise)
                l1 = 0.5 * revision_likelihood(y[t], x[t], context[t], 0, 1, cfg.revision_noise)
                l1 += 0.5 * revision_likelihood(y[t], x[t], context[t], 1, 1, cfg.revision_noise)
            else:
                assert observed_action is not None
                a = int(observed_action[t])
                l0 = revision_likelihood(y[t], x[t], context[t], a, 0, cfg.revision_noise)
                l1 = revision_likelihood(y[t], x[t], context[t], a, 1, cfg.revision_noise)
            p_h1 = posterior_binary(p_h1, l0, l1)
            area += p_h1
        return (area / n) if p_h1 > 0.5 else 0.0

    e = learn(y_e, command_e, integrate_action=False)
    return {
        "A": learn(y_a, action_a, integrate_action=False),
        "B_E": learn(y_e, None, integrate_action=True),
        "C_E": e,
        "D": learn(y_d, command_e, integrate_action=False),
        "E": e,
    }


def fault_likelihood(y: int, command: int, fault: int, cfg: StudyConfig) -> float:
    p_one = cfg.fault_hit if command == fault else cfg.fault_false_alarm
    return p_one if y == 1 else (1.0 - p_one)


def choose_eig_action(prior: np.ndarray, cfg: StudyConfig) -> int:
    best_action, best_gain = 0, -math.inf
    prior_entropy = entropy(prior)
    for action in range(5):
        p_y1_by_fault = np.array(
            [cfg.fault_hit if action == f else cfg.fault_false_alarm for f in range(5)],
            dtype=float,
        )
        p_y1 = float(np.dot(prior, p_y1_by_fault))
        expected_entropy = 0.0
        for y, p_y in ((1, p_y1), (0, 1.0 - p_y1)):
            likelihood = p_y1_by_fault if y == 1 else (1.0 - p_y1_by_fault)
            post = prior * likelihood
            post /= post.sum()
            expected_entropy += p_y * entropy(post)
        gain = prior_entropy - expected_entropy
        if gain > best_gain + 1e-15:
            best_action, best_gain = action, gain
    return best_action


def update_fault(prior: np.ndarray, y: int, command: int, cfg: StudyConfig) -> np.ndarray:
    likelihood = np.array(
        [fault_likelihood(y, command, f, cfg) for f in range(5)], dtype=float
    )
    post = prior * likelihood
    return post / post.sum()


def simulate_fault_anchor(rng: np.random.Generator, cfg: StudyConfig) -> tuple[int, dict[str, int]]:
    n = cfg.fault_steps
    fault = int(rng.integers(0, 5))
    command_e = balanced_multiclass(rng, n, 5)
    action_d = restricted_permutation(rng, command_e, max_match_rate=0.10)
    u = rng.random(n)

    def observe(executed: int, t: int) -> int:
        p = cfg.fault_hit if executed == fault else cfg.fault_false_alarm
        return int(u[t] < p)

    y_e = np.array([observe(int(command_e[t]), t) for t in range(n)], dtype=int)
    y_d = np.array([observe(int(action_d[t]), t) for t in range(n)], dtype=int)

    def learn_tagged(y: np.ndarray, command: np.ndarray) -> int:
        prior = np.full(5, 0.2)
        for t in range(n):
            prior = update_fault(prior, int(y[t]), int(command[t]), cfg)
        winners = np.flatnonzero(np.isclose(prior, prior.max()))
        return int(rng.choice(winners))

    def learn_untagged() -> int:
        return int(rng.integers(0, 5))

    def learn_active() -> int:
        prior = np.full(5, 0.2)
        for t in range(n):
            action = choose_eig_action(prior, cfg)
            y = observe(action, t)
            prior = update_fault(prior, y, action, cfg)
        winners = np.flatnonzero(np.isclose(prior, prior.max()))
        return int(rng.choice(winners))

    e_pred = learn_tagged(y_e, command_e)
    return fault, {
        "A": learn_active(),
        "B_E": learn_untagged(),
        "C_E": e_pred,
        "D": learn_tagged(y_d, command_e),
        "E": e_pred,
    }


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, k: int = 5) -> float:
    values = []
    for label in range(k):
        tp = np.sum((y_true == label) & (y_pred == label))
        fp = np.sum((y_true != label) & (y_pred == label))
        fn = np.sum((y_true == label) & (y_pred != label))
        den = 2 * tp + fp + fn
        values.append((2 * tp / den) if den else 0.0)
    return float(np.mean(values))


def simulate_dataset(n: int, seed: int, cfg: StudyConfig) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    revision = {condition: np.empty(n, dtype=float) for condition in CONDITIONS}
    fault_true = np.empty(n, dtype=int)
    fault_pred = {condition: np.empty(n, dtype=int) for condition in CONDITIONS}
    for i in range(n):
        rev = simulate_revision_anchor(rng, cfg)
        for condition in CONDITIONS:
            revision[condition][i] = rev[condition]
        true, pred = simulate_fault_anchor(rng, cfg)
        fault_true[i] = true
        for condition in CONDITIONS:
            fault_pred[condition][i] = pred[condition]
    return {"revision": revision, "fault_true": fault_true, "fault_pred": fault_pred}


def estimate(dataset: dict[str, object], indices: np.ndarray | None = None) -> dict[str, dict[str, float]]:
    revision = dataset["revision"]
    fault_true = dataset["fault_true"]
    fault_pred = dataset["fault_pred"]
    assert isinstance(revision, dict) and isinstance(fault_pred, dict)
    assert isinstance(fault_true, np.ndarray)
    if indices is None:
        indices = np.arange(len(fault_true))
    out = {"gated_revision_recovery": {}, "fault_macro_f1": {}}
    for name, (left, right) in CONTRASTS.items():
        out["gated_revision_recovery"][name] = float(
            np.mean(revision[left][indices] - revision[right][indices])
        )
        out["fault_macro_f1"][name] = macro_f1(
            fault_true[indices], fault_pred[left][indices]
        ) - macro_f1(fault_true[indices], fault_pred[right][indices])
    return out


def bootstrap_intervals(dataset: dict[str, object], cfg: StudyConfig) -> dict[str, dict[str, tuple[float, float]]]:
    rng = np.random.default_rng(cfg.seed + 91)
    n = len(dataset["fault_true"])
    draws = {
        outcome: {name: np.empty(cfg.n_bootstrap) for name in CONTRASTS}
        for outcome in ("gated_revision_recovery", "fault_macro_f1")
    }
    for b in range(cfg.n_bootstrap):
        idx = rng.integers(0, n, n)
        est = estimate(dataset, idx)
        for outcome in draws:
            for name in CONTRASTS:
                draws[outcome][name][b] = est[outcome][name]
    return {
        outcome: {
            name: tuple(np.quantile(values, [0.025, 0.975]).tolist())
            for name, values in by_name.items()
        }
        for outcome, by_name in draws.items()
    }


def flatten_results(finite, reference, intervals) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for outcome in finite:
        for contrast in CONTRASTS:
            lo, hi = intervals[outcome][contrast]
            truth = reference[outcome][contrast]
            rows.append(
                {
                    "outcome": outcome,
                    "contrast": contrast,
                    "estimate": finite[outcome][contrast],
                    "ci_low": lo,
                    "ci_high": hi,
                    "monte_carlo_reference": truth,
                    "reference_covered": bool(lo <= truth <= hi),
                }
            )
    return rows


def condition_estimates(dataset: dict[str, object]) -> dict[str, dict[str, float]]:
    revision = dataset["revision"]
    fault_true = dataset["fault_true"]
    fault_pred = dataset["fault_pred"]
    assert isinstance(revision, dict) and isinstance(fault_pred, dict)
    assert isinstance(fault_true, np.ndarray)
    return {
        "gated_revision_recovery": {
            condition: float(np.mean(revision[condition])) for condition in CONDITIONS
        },
        "fault_macro_f1": {
            condition: macro_f1(fault_true, fault_pred[condition]) for condition in CONDITIONS
        },
    }


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    cfg = StudyConfig()
    finite_data = simulate_dataset(cfg.n_finite, cfg.seed, cfg)
    reference_data = simulate_dataset(cfg.n_reference, cfg.seed + 1, cfg)
    finite = estimate(finite_data)
    reference = estimate(reference_data)
    intervals = bootstrap_intervals(finite_data, cfg)
    rows = flatten_results(finite, reference, intervals)

    write_csv(args.output_dir / "synthetic_estimand_recovery.csv", rows)
    metadata = {
        "study": "Perceptual Twins minimal synthetic estimand-recovery study",
        "scope": "Resettable one-step microenvironment; not a full benchmark validation",
        "configuration": cfg.__dict__,
        "all_reference_values_covered": all(bool(row["reference_covered"]) for row in rows),
        "finite_sample_condition_estimates": condition_estimates(finite_data),
        "reference_condition_estimates": condition_estimates(reference_data),
        "results": rows,
    }
    with (args.output_dir / "synthetic_estimand_recovery.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    for row in rows:
        print(
            f"{row['outcome']:24s} {row['contrast']:16s} "
            f"estimate={row['estimate']:+.3f} "
            f"95% CI [{row['ci_low']:+.3f}, {row['ci_high']:+.3f}] "
            f"reference={row['monte_carlo_reference']:+.3f} "
            f"covered={row['reference_covered']}"
        )


if __name__ == "__main__":
    main()
