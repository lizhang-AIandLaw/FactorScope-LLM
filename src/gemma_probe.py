"""RQ1/RQ2 readouts for Gemma-2 2B with Gemma Scope JumpReLU SAEs.

Extract residual activations at about 25/50/75% depth, encode with the width-16k SAE whose
average L0 is closest to 100, and fit raw, top-1, top-5, and random-5 readouts on the same splits.

Output: artifacts/probes/gemma-2-2b.json
"""
import json
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from huggingface_hub import hf_hub_download, list_repo_files  # noqa: E402
from scipy.stats import rankdata  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

ROOT = os.environ.get("FS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL = "google/gemma-2-2b"
SAE_REPO = "google/gemma-scope-2b-pt-res"
LAYERS = [6, 13, 20]


def pick_sae_paths():
    files = list_repo_files(SAE_REPO)
    out = {}
    for L in LAYERS:
        cands = []
        for f in files:
            if f.startswith(f"layer_{L}/width_16k/average_l0_") and f.endswith("params.npz"):
                l0 = int(f.split("average_l0_")[1].split("/")[0])
                cands.append((abs(l0 - 100), l0, f))
        _, l0, path = min(cands)
        out[L] = (l0, path)
        print(f"[gemma] layer {L}: using {path}")
    return out


def jumprelu_encode(resid, p):
    pre = resid @ p["W_enc"] + p["b_enc"]
    return np.where(pre > p["threshold"], np.maximum(pre, 0.0), 0.0)


def topk_by_auc(X, y, k):
    ranks = rankdata(X, axis=0)
    n1 = int(y.sum())
    n0 = len(y) - n1
    r1 = ranks[y == 1].sum(axis=0)
    with np.errstate(all="ignore"):
        aucs = (r1 - n1 * (n1 + 1) / 2) / (n1 * n0)
    aucs = np.where(X.std(axis=0) > 0, aucs, 0.5)
    return np.argsort(np.abs(aucs - 0.5))[::-1][:k]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--factors", default="F6,F16")
    ap.add_argument("--filtered-dir", default=f"{ROOT}/data/classification")
    ap.add_argument("--out", default=f"{ROOT}/artifacts/probes/gemma-2-2b.json")
    args = ap.parse_args()
    FACTORS = args.factors.split(",")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    assert device == "cuda"
    rows = []
    for fid in FACTORS:
        rows += [json.loads(line) for line in open(f"{args.filtered_dir}/{fid}/pos.jsonl")]
    rows += [json.loads(line) for line in open(f"{args.filtered_dir}/neutral.jsonl")]
    print(f"[gemma] {len(rows)} rows")

    sae_paths = pick_sae_paths()
    saes = {}
    for L, (l0, path) in sae_paths.items():
        z = np.load(hf_hub_download(SAE_REPO, path))
        saes[L] = {k: z[k].astype(np.float32) for k in ("W_enc", "W_dec", "b_enc", "b_dec", "threshold")}

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32)
    model.eval().to(device)

    captured, hooks = {}, []
    for L in LAYERS:
        def mk(L):
            def hook(m, i, o):
                captured[L] = (o[0] if isinstance(o, tuple) else o).detach()
            return hook
        hooks.append(model.model.layers[L].register_forward_hook(mk(L)))

    feats = {L: [] for L in LAYERS}
    raw = {L: [] for L in LAYERS}
    with torch.no_grad():
        for i, r in enumerate(rows):
            inputs = tok(r["text"], return_tensors="pt", truncation=True, max_length=256).to(device)
            model(**inputs)
            for L in LAYERS:
                resid = captured[L].float()[0].cpu().numpy()
                body = resid[1:] if resid.shape[0] > 1 else resid
                raw[L].append(body.mean(0))
                feats[L].append(jumprelu_encode(body, saes[L]).mean(0))
            if (i + 1) % 100 == 0:
                print(f"[gemma] {i+1}/{len(rows)}", flush=True)
    for h in hooks:
        h.remove()

    report = {"sae_choices": {str(L): sae_paths[L][1] for L in LAYERS}}
    is_tr = np.array([r.get("split") == "train" for r in rows])
    for fid in FACTORS:
        y = np.array([1 if r["factor"] == fid else 0 for r in rows])
        best = {}
        for L in LAYERS:
            Xr, Xs = np.stack(raw[L]), np.stack(feats[L])
            clf = LogisticRegression(max_iter=5000).fit(Xr[is_tr], y[is_tr])
            a_raw = roc_auc_score(y[~is_tr], clf.decision_function(Xr[~is_tr]))
            row = {"raw_auc": round(float(a_raw), 4)}
            for k in (1, 5):
                idx = topk_by_auc(Xs[is_tr], y[is_tr], k)
                c2 = LogisticRegression(max_iter=5000).fit(Xs[is_tr][:, idx], y[is_tr])
                row[f"top{k}_auc"] = round(float(
                    roc_auc_score(y[~is_tr], c2.decision_function(Xs[~is_tr][:, idx]))), 4)
                if k == 5:
                    row["top5_latents"] = [int(j) for j in idx]
            rng = np.random.default_rng(0)
            rnd = []
            for _ in range(20):
                idx = rng.choice(Xs.shape[1], 5, replace=False)
                c3 = LogisticRegression(max_iter=5000).fit(Xs[is_tr][:, idx], y[is_tr])
                rnd.append(roc_auc_score(y[~is_tr], c3.decision_function(Xs[~is_tr][:, idx])))
            row["random5_mean"] = round(float(np.mean(rnd)), 4)
            best[f"L{L}"] = row
            print(fid, f"L{L}", row, flush=True)
        report[fid] = best

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print("[gemma] done")


if __name__ == "__main__":
    main()
