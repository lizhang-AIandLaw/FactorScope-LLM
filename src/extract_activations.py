"""Extract residual and SAE feature activations for the corpus passages.

Saves one .pt per layer with mean-pool and last-token tensors + a manifest.

Usage:
  python src/extract_activations.py --data-dir data/classification \
      --factors F6,F16 --model Qwen/Qwen3-1.7B-Base \
      --sae Qwen/SAE-Res-Qwen3-1.7B-Base-W32K-L0_100 \
      --layers 7,14,21 --out artifacts/activations/qwen3-1.7b
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch  # noqa: E402
from huggingface_hub import hf_hub_download  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402


def read_rows(data_dir, factors):
    rows = []
    for fid in factors:
        with open(os.path.join(data_dir, fid, "pos.jsonl")) as f:
            rows += [json.loads(line) for line in f if line.strip()]
    with open(os.path.join(data_dir, "neutral.jsonl")) as f:
        rows += [json.loads(line) for line in f if line.strip()]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/classification")
    ap.add_argument("--factors", default="F6,F16")
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B-Base")
    ap.add_argument("--sae", default="Qwen/SAE-Res-Qwen3-1.7B-Base-W32K-L0_100")
    ap.add_argument("--layers", default="7,14,21")
    ap.add_argument("--k", type=int, default=100)
    ap.add_argument("--out", default="artifacts/activations/qwen3-1.7b")
    args = ap.parse_args()

    layers = [int(x) for x in args.layers.split(",")]
    rows = read_rows(args.data_dir, args.factors.split(","))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    assert device == "cuda", "no CUDA visible"
    print(f"[extract] {len(rows)} rows, layers {layers}, device {device}")

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float32)
    model.eval().to(device)

    saes = {}
    for L in layers:
        sd = torch.load(hf_hub_download(args.sae, f"layer{L}.sae.pt"), map_location=device)
        saes[L] = sd

    captured = {}
    hooks = []
    for L in layers:
        def mk(L):
            def hook(m, i, o):
                captured[L] = (o[0] if isinstance(o, tuple) else o).detach()
            return hook
        hooks.append(model.model.layers[L].register_forward_hook(mk(L)))

    store = {L: {"resid_mean": [], "resid_last": [], "sae_mean": [], "sae_last": []}
             for L in layers}
    meta = []
    with torch.no_grad():
        for i, r in enumerate(rows):
            inputs = tok(r["text"], return_tensors="pt", truncation=True, max_length=256).to(device)
            model(**inputs)
            for L in layers:
                resid = captured[L].float()[0]          # (seq, d)
                sd = saes[L]
                pre = resid @ sd["W_enc"].T + sd["b_enc"]
                vals, idx = pre.topk(args.k, dim=-1)
                acts = torch.zeros_like(pre).scatter_(-1, idx, vals)
                # exclude position 0 (BOS-like outlier norm) from mean pooling
                store[L]["resid_mean"].append(resid[1:].mean(0).cpu() if resid.shape[0] > 1
                                              else resid.mean(0).cpu())
                store[L]["resid_last"].append(resid[-1].cpu())
                store[L]["sae_mean"].append(acts[1:].mean(0).cpu() if acts.shape[0] > 1
                                            else acts.mean(0).cpu())
                store[L]["sae_last"].append(acts[-1].cpu())
            meta.append({k: r.get(k) for k in
                         ("factor", "label", "split", "industry", "secret_type", "style")})
            if (i + 1) % 25 == 0:
                print(f"[extract] {i+1}/{len(rows)}", flush=True)
    for h in hooks:
        h.remove()

    os.makedirs(args.out, exist_ok=True)
    for L in layers:
        payload = {k: torch.stack(v) for k, v in store[L].items()}
        nz = (payload["sae_last"] != 0).sum(-1).float().mean().item()
        torch.save(payload, os.path.join(args.out, f"layer{L}.pt"))
        print(f"[extract] layer{L}: sae_last mean-nonzero={nz:.1f} (k={args.k})")
    with open(os.path.join(args.out, "meta.jsonl"), "w") as f:
        for m in meta:
            f.write(json.dumps(m) + "\n")
    manifest = {
        "model": args.model, "sae": args.sae, "layers": layers, "k": args.k,
        "n_rows": len(rows), "data_dir": args.data_dir,
        "data_hash": hashlib.sha256("".join(r["text"] for r in rows).encode()).hexdigest()[:16],
        "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                 capture_output=True, text=True).stdout.strip(),
    }
    with open(os.path.join(args.out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("[extract] done ->", args.out)


if __name__ == "__main__":
    main()
