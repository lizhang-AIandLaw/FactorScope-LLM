"""TF-IDF logistic-regression baseline on the same train/test split as the probes.

Per factor: fit on the training partition (positives vs. neutral passages and
other factors' positives, excluding entailing factors) using unigram and
bigram TF-IDF features, then report AUC on the test partition.
"""
import json
import os
import sys

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.environ.get("FS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.environ.get("FS_TFIDF_DATA", f"{ROOT}/data/classification")
import factors as FZ  # noqa: E402
FZ.use_set(os.environ.get("FS_FACTOR_SET", "27"))
FACTORS = os.environ.get("FS_TFIDF_FACTORS", ",".join(FZ.ACTIVE)).split(",")


def rows_of(path):
    return [json.loads(line) for line in open(path)]


all_rows = []
for f in FACTORS:
    all_rows += rows_of(f"{DATA}/{f}/pos.jsonl")
all_rows += rows_of(f"{DATA}/neutral.jsonl")

texts = [r["text"] for r in all_rows]
is_tr = np.array([r["split"] == "train" for r in all_rows])

out = {}
for fid in FACTORS:
    y = np.array([1 if r["factor"] == fid else 0 for r in all_rows])
    mask = np.ones(len(all_rows), bool)
    ent = FZ.entailers_of(fid)
    if ent:
        mask &= np.array([r["factor"] not in ent for r in all_rows])
    vec = TfidfVectorizer(min_df=2, ngram_range=(1, 2))
    Xtr = vec.fit_transform([t for t, m, tr in zip(texts, mask, is_tr) if m and tr])
    ytr = y[mask & is_tr]
    clf = LogisticRegression(max_iter=2000, C=1.0).fit(Xtr, ytr)
    sel = mask & ~is_tr
    Xte = vec.transform([t for t, s in zip(texts, sel) if s])
    out[fid] = {"test_auc": round(float(roc_auc_score(y[sel], clf.decision_function(Xte))), 4)}
    print(fid, out[fid], flush=True)

os.makedirs(f"{ROOT}/artifacts/controls", exist_ok=True)
with open(f"{ROOT}/artifacts/controls/tfidf_baseline.json", "w") as f:
    json.dump(out, f, indent=2)
print("saved")
