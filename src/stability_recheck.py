"""Re-estimate top-five SAE feature stability with bootstrap resampling."""

import argparse
import json
import os
import sys

import numpy as np
import torch
from scipy.stats import rankdata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factors as FZ  # noqa: E402


ROOT = os.environ.get("FS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def topk(x, y, k=5):
    ranks = rankdata(x, axis=0)
    n_positive = int(y.sum())
    n_negative = len(y) - n_positive
    positive_rank_sum = ranks[y == 1].sum(axis=0)
    with np.errstate(all="ignore"):
        auc = (
            positive_rank_sum - n_positive * (n_positive + 1) / 2
        ) / (n_positive * n_negative)
    auc = np.where(x.std(axis=0) > 0, auc, 0.5)
    return set(int(index) for index in np.argsort(np.abs(auc - 0.5))[::-1][:k])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--acts", default=f"{ROOT}/artifacts/activations/qwen3-8b")
    parser.add_argument("--probe", default=f"{ROOT}/artifacts/probes/qwen3-8b.json")
    parser.add_argument("--factors", default="F2,F8,F11,F24")
    parser.add_argument("--bootstraps", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default=f"{ROOT}/artifacts/stability/qwen3-8b.json")
    args = parser.parse_args()

    FZ.use_set("27")
    meta = [json.loads(line) for line in open(os.path.join(args.acts, "meta.jsonl"))]
    probe = json.load(open(args.probe))["results"]
    rng = np.random.default_rng(args.seed)
    output = {}

    for factor in args.factors.split(","):
        layer = int(
            max(
                (values["raw_auc"], key)
                for key, values in probe.items()
                if key.startswith(factor + "/")
            )[1].split("/L")[1]
        )
        features = torch.load(os.path.join(args.acts, f"layer{layer}.pt"))["sae_mean"].numpy()
        labels = np.array([1 if row["factor"] == factor else 0 for row in meta])
        train = np.array([row["split"] == "train" for row in meta])
        entailers = FZ.entailers_of(factor)
        if entailers:
            train &= np.array([row["factor"] not in entailers for row in meta])
        train_indices = np.where(train)[0]
        selections = []
        for _ in range(args.bootstraps):
            sample = rng.choice(train_indices, len(train_indices), replace=True)
            selections.append(topk(features[sample], labels[sample]))
        jaccards = [
            len(left & right) / len(left | right)
            for index, left in enumerate(selections)
            for right in selections[index + 1 :]
        ]
        output[factor] = {
            "layer": layer,
            "n_bootstraps": args.bootstraps,
            "mean_pairwise_top5_jaccard": round(float(np.mean(jaccards)), 4),
        }
        print(factor, output[factor], flush=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as handle:
        json.dump(output, handle, indent=2)


if __name__ == "__main__":
    main()
