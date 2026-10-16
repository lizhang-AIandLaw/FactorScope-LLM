"""RQ1/RQ2 readouts on extracted residual and SAE activations.

Per factor and per sampled layer:
  RQ1: L2 logistic classifier on the mean-pooled residual vector (raw_auc).
  RQ2: top-1 and top-5 SAE features, ranked on the training partition by
       |AUC - 0.5|, each refitted with an L2 logistic readout (top1_auc,
       top5_auc), plus a random-5 reference averaged over 20 draws.
Negatives = neutral passages + other factors' positives, excluding factors
that entail the target. The train/test split comes from the data.

Usage:
  python src/probe.py --acts artifacts/activations/qwen3-1.7b --factors F6,F16 \
      --report artifacts/probes/qwen3-1.7b.md
"""
import argparse
import json
import os
import sys

import numpy as np
import torch
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factors as FZ  # noqa: E402


def auc_probe(Xtr, ytr, Xte, yte, C=1.0, seed=0):
    clf = LogisticRegression(max_iter=5000, C=C, random_state=seed)
    clf.fit(Xtr, ytr)
    return roc_auc_score(yte, clf.decision_function(Xte)), clf


def rank_features(X, y):
    """Rank SAE features by |AUC - 0.5| on the training partition.

    Uses the Mann-Whitney U identity AUC = (R1 - n1(n1+1)/2) / (n1*n0).
    Constant features receive 0.5.
    """
    ranks = rankdata(X, axis=0)
    n1 = int(y.sum())
    n0 = len(y) - n1
    r1 = ranks[y == 1].sum(axis=0)
    with np.errstate(all="ignore"):
        aucs = (r1 - n1 * (n1 + 1) / 2) / (n1 * n0)
    aucs = np.where(X.std(axis=0) > 0, aucs, 0.5)
    return np.argsort(np.abs(aucs - 0.5))[::-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts", default="artifacts/activations/qwen3-1.7b")
    ap.add_argument("--factors", default="F6,F16")
    ap.add_argument("--pooling", default="mean", choices=["mean", "last"])
    ap.add_argument("--report", default="artifacts/probes/qwen3-1.7b.md")
    ap.add_argument("--seed", type=int, default=0)
    FZ.add_set_arg(ap)
    args = ap.parse_args()
    FZ.use_set(args.factor_set)

    rng = np.random.default_rng(args.seed)
    meta = [json.loads(line) for line in open(os.path.join(args.acts, "meta.jsonl"))]
    manifest = json.load(open(os.path.join(args.acts, "manifest.json")))
    layers = manifest["layers"]
    factors = args.factors.split(",")
    suffix = "mean" if args.pooling == "mean" else "last"

    results = {}
    lines = [f"# Probe report\n\nacts={args.acts} pooling={args.pooling} "
             f"model={manifest['model']}\ncommit={manifest['commit']} "
             f"data_hash={manifest['data_hash']}\n"]
    for L in layers:
        data = torch.load(os.path.join(args.acts, f"layer{L}.pt"))
        Xr = data[f"resid_{suffix}"].numpy()
        Xs = data[f"sae_{suffix}"].numpy()
        for fid in factors:
            y = np.array([1 if m["factor"] == fid else 0 for m in meta])
            is_tr = np.array([m["split"] == "train" for m in meta])
            # Exclude entailed positives from the negative pool: a factor X
            # that entails fid also satisfies fid, so X's positives are not
            # valid negatives for fid (for example F25 => F16).
            mask = np.ones(len(meta), bool)
            entailing = FZ.entailers_of(fid)
            if entailing:
                mask &= np.array([m["factor"] not in entailing for m in meta])
            tr, te = is_tr & mask, ~is_tr & mask
            row = {}
            a_raw, _ = auc_probe(Xr[tr], y[tr], Xr[te], y[te], seed=args.seed)
            row["raw_auc"] = a_raw
            order = rank_features(Xs[tr], y[tr])
            for k in (1, 5):
                idx = order[:k]
                a_k, _ = auc_probe(Xs[tr][:, idx], y[tr], Xs[te][:, idx], y[te], seed=args.seed)
                row[f"top{k}_auc"] = a_k
                row[f"top{k}_latents"] = [int(j) for j in idx]
            rnd_aucs = []
            for _ in range(20):
                idx = rng.choice(Xs.shape[1], 5, replace=False)
                a_r, _ = auc_probe(Xs[tr][:, idx], y[tr], Xs[te][:, idx], y[te], seed=args.seed)
                rnd_aucs.append(a_r)
            row["random5_auc_mean"] = float(np.mean(rnd_aucs))
            results[f"{fid}/L{L}"] = {k: (round(v, 4) if isinstance(v, float) else v)
                                      for k, v in row.items()}
            lines.append(
                f"- **{fid} layer {L}**: raw={a_raw:.3f} "
                f"top1={row['top1_auc']:.3f} top5={row['top5_auc']:.3f} "
                f"rand5={row['random5_auc_mean']:.3f}")
            print(lines[-1], flush=True)

    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    # match on "<fid>/" so F1 does not also capture F16/F18's keys
    best_raw = {fid: max(v["raw_auc"] for k, v in results.items()
                         if k.startswith(fid + "/"))
                for fid in factors}
    lines.append(f"\n## Best-layer raw AUC per factor: {best_raw}")
    with open(args.report, "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(args.report.replace(".md", ".json"), "w") as f:
        json.dump({"results": results, "best_raw": best_raw,
                   "manifest": manifest}, f, indent=2)
    print(f"[probe] -> {args.report}")


if __name__ == "__main__":
    main()
